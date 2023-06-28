# Benndot's Arcade Shooter 2.0

An attempt at making a two-dimensional arcade-style shooting game. 

## Game Overview

The game is currently story-less, but currently centers around a "suburban dad" stereotype character facing off against
a hoard of hippies.

The gameplay is that of a classic 2D vertical shooter, where the player moves back and forth on the x-axis and fires 
projectiles at enemies located above. Left and right movement is performed either with arrow keys or WASD. Each press of
the space bar launches a projectile, though the number of projectiles allowed at once are limited. 

## Current State

Core gameplay has been implemented, but the game loops has not been completed. The player can move and shoot, and the 
enemies will be generated, will move and can be hit by the player's projectile's. However, there is currently no way to 
lose, and no trigger for victory. 

The game works in multiple resolutions and can be swapped between resolutions during gameplay. All visual aspects scale
properly between resolutions, but the functionality is new and may have undiscovered bugs. 

## Controls

Movement: WASD or Arrow Keys

Shoot: Space

Return to menu: Esc

Mute music: M

## todo

iterate through enemy details dict in order to list of their health and images in the right margin

move player object from stage to game or elsewhere

add enemy collision and player health loss

implement victory and defeat scenarios

add sound effect volume controls, simplify/improve music system

turn player projectile limit into a time-based cooldown

introduce more stages and more enemy types

implement proper pre-game set up and post-game/post-return-to-menu resets

create settings menu with sound options and screen resizing