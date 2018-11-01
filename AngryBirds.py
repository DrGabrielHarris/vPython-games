"""
Author: Dr. M.G.Alhrishy (mazen.alhrishy@gmail.com)

A game with mechanics similar to Angry Birds. The player launches a projectile at a target to try to topple it
In order to do this, the following has been simulated:

1- the projectile path
2- the momentum of the projectile at the point of impact with the target
3- the impulse transferred to the target
4- the torque on the target due to the collision, and whether or not this is greater than the restoring torque
"""
import numpy as np
from vpython import sphere, color, rate, canvas, vector, curve, label, box, cross, mag, random, arrow

g = 9.81  # gravitational acceleration, m/s2
dt = 0.01  # contact time

target_m = 100  # kg

# --------------------------------------------- draw the scene ---------------------------------------------------------
scene = canvas(width=640, height=480, center=vector(8, 0, 0), range=8)
ground = curve(pos=[(0, 0, 0), (16, 0, 0)], color=color.green)
user_label = label(pos=vector(0, 5, 0), visible=False, xoffset=2, text='')

# --------------------------------------------- target's attributes ----------------------------------------------------
# generate a random x-pos
target_x = 15*random()
if target_x < 5:
    target_x = 5

# draw the target
target_w = 0.5  # in m
target_h = 2  # i m
target = box(pos=vector(target_x, 1, 0), length=0.5, height=target_h, width=target_w, opacity=0.5)

# calculate the target centre of rotation
target_cor = vector(target.pos.x + target_w/2, 0, 0)

# ---------------------------------------------- bird's attributes------------------------------------------------------
bird_m = 0.1  # bird mass in kg
bird_rad = 0.05  # bird radius in m
bird_x0 = bird_x = 0.0
bird_y0 = bird_y = 0.0
bird = sphere(pos=vector(bird_x0, bird_y0, 0), radius=0.3, color=color.red, make_trail=True, opacity=0.5)

# ---------------------------------------------- hit attributes---------------------------------------------------------
hit_tolerance = bird_rad + (target_w/2)  # in m

# for drawing the da arrow later (it's not visible for now) when the bird hits the target
da_arrow = arrow(pos=target_cor, visible=False, color=color.red, shaftwidth=0.1)

# calculate the restoring torque (as a magnitude)
restoring_t_mag = -target_m * g * (target_w/2)

# ---------------------------------------------- ask user forever unless toppled ---------------------------------------
while True:
    # initialize these every new try
    t = 0  # initial time
    bird_x = bird_x0
    bird_y = bird_y0
    toppled = False
    hit = False

    # input initial angle and speed from user
    theta = np.radians(float(input("Input the initial angle in degrees: ")))
    v0 = float(input("Input the initial speed in metres/second: "))

    # clear bird position and it's trail
    bird.clear_trail()
    bird.pos = vector(bird_x, bird_y, 0)
    user_label.visible = False
    da_arrow.visible = False

    # check if the bird has hit the ground yet or not, and if it has passed the target x-pos
    while (bird_y >= 0) and (bird_x <= target.pos.x):
        rate(5)

        # update the current bird position
        t = t + dt
        bird_x = bird_x0 + v0 * t * np.cos(theta)
        bird_y = bird_y0 + v0 * t * np.sin(theta) - 0.5 * g * t * t
        bird.pos = vector(bird_x, bird_y, 0)

        # check if the bird has hit the target
        if (np.abs(bird_x - target_x) < hit_tolerance) and (bird_y <= target_h):
            hit = True

            # calculate the current bird position momentum
            bird_px = bird_m * v0 * np.cos(theta)
            bird_py = bird_m * v0 * np.sin(theta) - bird_m * g * t
            bird_p = vector(bird_px, bird_py, 0)

            # calculate the current bird position applied force
            applied_f = bird_p / dt

            # calculate the vector from the target's point of rotation to the point of impact and draw it
            da = vector(target_cor.x - bird_x, bird_y, 0)
            da_arrow.visible = True
            da_arrow.axis = vector(bird_x, bird_y, 0) - target_cor

            # calculate the current bird position applied torque (as a vector then as a magnitude)
            applied_t = cross(applied_f, da)
            applied_t_mag = mag(applied_t)

            print('Height of the impact point:', bird_y)  # distance h
            print("Bird's momentum at the point of impact:", bird_m)
            print('Applied torque', applied_t)
            print('Magnitude of the restoring torque', restoring_t_mag)

            # check if the applied force is enough to topple the target, and rotate if toppled
            # if not toppled, break while loop
            if applied_t_mag > abs(restoring_t_mag):
                toppled = True
                target.rotate(angle=np.radians(270), axis=vector(0, 0, 1), origin=target_cor)
                break
            else:
                break

    # make the label visible for the user
    user_label.visible = True

    if toppled:
        user_label.text = "The target has been toppled!"
        break
    elif hit:
        user_label.text = "The target has been hit but not toppled!"
    else:
        user_label.text = "The target has been missed! Try again!"
