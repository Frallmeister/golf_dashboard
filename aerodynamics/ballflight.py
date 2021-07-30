from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from logger import log

MOLAR_MASS = 28.9647/1000       # [kg/mol]
BALL_RADIUS = 0.5*42.67/1000    # [m]
BALL_MASS = 45.93/1000          # [kg]
R = 8.3144                      # [J/mol/K]
TIME_STEP = 0.05


def c_drag(reynolds, mode=None, **kwargs):
    """
    Returns the coefficient of drag based on figure 2b in 
    "Aerodynamics of Golf Balls in Still Air"; Bin, Lyu et al (2018)
    """

    if mode==None or mode=='spline':
        # Estimate CD as a cubic interpolation
        Re_val = np.array([0.001, 10, 0.5, 0.64, 0.8, 0.96, 1.12, 1.5])*1e5
        cd_val = np.array([0.62, 0.5, 0.65, 0.6, 0.41, 0.38, 0.39, 0.41])
        if kwargs.get('cd') is not None:
            cd_val = kwargs.get('cd')
            Re_val = Re_val[:len(cd_val)]
        cd = interp1d(Re_val, cd_val, 'cubic')
        return cd(reynolds)
    elif mode=='poly':
        # Treat CD as a polynomial
        coeff = np.array([5.86, -1.676e-4, 1.699e-9, -5.697e-15])
        if kwargs.get('coeff') is not None:
            coeff = kwargs.get('coeff')
        Re = np.array([reynolds**i for i in range(len(coeff))])
        return sum(Re*coeff)
    else:
        raise Exception("mode must be either 'poly' or 'spline'")

    # c=0.2
    # if reynolds < 81207.6:
    #     return 1.29*10**(-10)*reynolds**2 - 2.59*10**(-5)*reynolds + 1.50 + c
    # else:
    #     return 1.91*10**(-11)*reynolds**2 - 5.40*10**(-6)*reynolds + 0.56 + c


def c_lift(spin, velocity):
    """
    From: "Aerodynamics of Golf Balls in Still Air"; Lyu (2018)
    """
    spin_norm = np.linalg.norm(spin)
    v_norm = np.linalg.norm(velocity)
    S = 2*np.pi*spin_norm*BALL_RADIUS / v_norm
    # return -3.25*S**2 + 1.99*S
    return -0.05 + np.sqrt(0.0025 + 0.36*BALL_RADIUS*2*np.pi*spin_norm/v_norm)


def density(P, T, RH=0):
    """
    Returns the dry air density in kg/m3.
    P: (int) Pressure in Pa
    T: (int) Temperature in K
    RH: (float) Relative humidity
    """
    p_vapor = RH * sat_vapor_pressure(T)
    p_dry = P-p_vapor
    M_water = 0.018016

    return (p_dry*MOLAR_MASS + p_vapor*M_water) / (R*T)


def sat_vapor_pressure(T):
    """
    Calculate the saturation vapor pressure with Tetens' equation.
    """
    T_C = T-273
    return 1000 * 0.61078 * np.exp(17.27*T_C/(T_C+237.3))


def reynolds(velocity, density, diameter, viscosity):
    """
    Returns the Reynolds number

    velocity: (int, array) Flow speed [m/s]
    density: (int) Air density [kg/m3]
    diameter: (int) Ball diameter [m]
    viscosity: (int) Dynamic viscosity [Pa*s]
    """
    v_norm = np.linalg.norm(velocity)
    return density*v_norm*diameter/viscosity


def dyn_viscosity(T):
    """
    Returns the dynamic viscosity [Pa*s]
    T: (int) Temperature in Kelvin

    From Wikipedia: https://en.wikipedia.org/wiki/Viscosity#Air
    """
    return 2.791 * 10**(-7) * T**(0.7355)


def drag_force(Cd, P, T, v):
    """
    Returns a force vektor with the same dimensions as v.

    Cd: (int) Coefficient of drag
    P: (int) Air pressure [Pa]
    T: (int) Air temperature [K]
    v: (int, array) Ball velocity, can be a vector [m/s]
    """
    Ap = np.pi * BALL_RADIUS**2
    v_unit = v/np.linalg.norm(v)
    return Ap * MOLAR_MASS * Cd * P / (2 * R * T) * np.linalg.norm(v)**2 * -v_unit


def gravity_force(m):
    return m * np.array([0, 0, -9.82])


def lift(spin, velocity, rho):
    """
    Returns lift as a vektor perpendicular to the flow speed.
    From: "On the aerodynamic forces on a baseball with aplications", Santos (2018)
    """
    spin_norm = np.linalg.norm(spin)
    if spin_norm == 0:
        return np.array([0,0,0])
    Ap = np.pi * BALL_RADIUS**2
    
    lift_direction = np.cross(spin, velocity)
    lift_unit = lift_direction / np.linalg.norm(lift_direction)
    
    v_norm = np.linalg.norm(velocity)
    cos_spin_v_angle = np.dot(spin, velocity) / (spin_norm * v_norm)
    spin_v_angle = np.arccos(cos_spin_v_angle)

    Cl = c_lift(spin, velocity)
    return (1/2) * rho*Ap*Cl*v_norm**2 * np.sin(spin_v_angle)*lift_unit


def magnus_force(spin, velocity, rho):
    """
    Returns the magnus force as a vektor.

    spin: (array) Revolutions per second [1/sec]
    velocity: (array) Ball speed [m/s]
    rho: (int) Air density [kg/m3]
    """
    return 16/3 * np.pi**2 * BALL_RADIUS**3 * rho * np.cross(spin, velocity)


def run(v0, P, T, spin, **kwargs):
    """
    kwargs:
        mode: ['spline', 'poly'],
        cd: array (only if mode='spline')
        coeff: array (only if mode='poly')
        fetch: ['spin', 'Re', 'Cd', 'F_drag', 'F_lift']
    """
    dt = TIME_STEP

    position = np.array([[0, 0, 0]])
    v = np.array([v0])
    mu = dyn_viscosity(T)
    rho = density(P, T)
    weight = gravity_force(BALL_MASS)

    spin_decay = (1-0.04)**dt       # 4 % decay per second, (Lyu, 2018)

    fetch = kwargs.get('fetch', [])
    s = pd.Series(dtype='object')
    for i in fetch:
        # s[i] = np.array([])
        s[i] = np.nan
    df = pd.DataFrame([s]) if fetch else pd.DataFrame()

    while position[-1][-1] >= 0:
        Re = reynolds(v[-1], rho, 2*BALL_RADIUS, mu)
        Cd = c_drag(Re, **kwargs)
        F_drag = drag_force(Cd, P, T, v[-1])
        # F_lift = magnus_force(spin, v[-1], rho)
        F_lift = lift(spin, v[-1], rho)

        new_position = position[-1] + v[-1] * dt
        new_velocity = v[-1] + (weight + F_drag + F_lift)/BALL_MASS * dt

        v = np.append(v, [new_velocity], axis=0)
        position = np.append(position, [new_position], axis=0)
        spin = np.multiply(spin, spin_decay)

        if fetch:
            s = pd.Series([], dtype='object')
            for i in fetch:
                s[i] = locals()[i]
            df = df.append(s, ignore_index=True)

    df.insert(0, 'position', list(position))
    df.insert(1, 'velocity', list(v))
    df['density'] = rho
    df['viscosity'] = mu
    return df


def plot_cd(start=0.5*1e5, end=1*1e6, **kwargs):
    Re = np.linspace(start, end)
    cd = np.array([c_drag(i, **kwargs) for i in Re])
    plt.plot(Re*10**(-5), cd)
    plt.grid()
    plt.title("Coefficient of drag")
    plt.xlabel("Re*1e-5")
    plt.ylabel("CD")
    # plt.ylim([0.2, 0.8])
    plt.show()
    return cd


def plot_ballpath(pos):
    fig, (ax1, ax2) = plt.subplots(2,1)

    x = [p[0] for p in pos]
    y = [p[1] for p in pos]
    z = [p[2] for p in pos]

    ax1.plot(y, z)
    ax1.grid()
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("Height (m)")
 
    ax2.plot(y, x)
    ax2.grid()
    ax2.set_xlabel("Distance (m)")
    ax2.set_ylabel("Side (m)")
    ax2.invert_yaxis()
    plt.show()


def plot_forces(**kwargs):
    if not kwargs:
        return None
    
    i=0
    fig, ax = plt.subplots(1,4)
    for k, v in kwargs.items():
        print(f"sum({k}) = {sum(v)}")
        ax[i].plot(v)
        ax[i].grid()
        ax[i].set_title(k)
        i+=1
    plt.show()


def landing_angle(v):
    vx, vy, vz = v[-1]
    angle = np.arctan(vz/vy) + np.pi/2
    return round(angle*180/np.pi, 1)


def carry(pos):
    return round(pos[-1][1], 2)


def hang_time(pos):
    return round(TIME_STEP * len(pos), 2)


def height(pos):
    return round(max([p[2] for p in pos]), 2)


if __name__ == '__main__':
    t1 = time.time()
    P = 90000
    P = 101325
    T = 273+21
    
    # Velocity
    v_angle = 18.4 * np.pi/180
    v0 = 49.71 * np.array([0, np.cos(v_angle), np.sin(v_angle)])

    # Spin
    spin = np.array([4429, 0, 0]) / 60

    # Run
    df = run(v0, P, T, spin, fetch=['spin', 'Re', 'Cd'])
    pos = df['position'].to_numpy()
    v = df['velocity'].to_numpy()

    print("T =", T)
    print("P =", P)
    print("Height:", height(pos))
    print("distance:", carry(pos))
    print("Hang time:", hang_time(pos))
    print(f"Elapsed time: {round(time.time()-t1, 3)} seconds")