# Benndot's Arcade Shooter 2.0

An attempt at making a two-dimensional arcade-style shooting game. 

## Game Overview

The gameplay is that of a classic 2D vertical shooter, where the player moves back and forth on the x-axis and fires 
projectiles at enemies located above. Left and right movement is performed either with arrow keys or WASD. Each press of
the space bar launches a projectile, though the number of projectiles allowed at once are limited. 

The game's setting is a cartoon-ish depiction of the 1960's. The plot scenario is of a stereotypical suburban dad facing
off against a group of hippies, armed with nothing but a sport bag full of baseballs. 

## Current State

Core gameplay has been implemented, but it lacks a proper game loop. The player can move and shoot, and the enemies 
will be generated, will move and can be hit by the player's projectiles. The amount of enemies remaining is tracked in
a user interface, as is the current stage. 

Defeating every enemy reveals a win screen that allows the player to return to the main menu. There is currently no way 
to lose and no existing game scenario for losing. 

Two stages currently exist, but there is currently no way to access both during the same play session.

The settings menu accessible from the start menu allows the user to change the sound effect volume. 

The game works in multiple resolutions and can be swapped between resolutions during gameplay. All visual aspects scale
properly between resolutions, but the functionality is new and may have undiscovered bugs. 

## Controls

Movement: WASD or Arrow Keys

Shoot: Space

Return to menu: Esc

Mute music: M (in-game only)

## todo

iterate through enemy details dict in order to list of their health and images in the right margin

move player object from stage to game or elsewhere

add enemy collision and player health loss

improve victory scenario, implement defeat scenario

turn player projectile limit into a time-based cooldown

introduce more stages and more enemy types

implement proper pre-game set up and post-game/post-return-to-menu resets

create settings menu with sound options and screen resizing