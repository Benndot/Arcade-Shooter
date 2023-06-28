# Benndot's Arcade Shooter 2.0

An attempt at making a two-dimensional arcade-style shooting game. 

## Game Overview

The game is currently story-less, but currently centers around a "suburban dad" stereotype character facing off against
a hoard of hippies.

The gameplay is that of a classic 2D vertical shooter, where the player moves back and forth on the x-axis and fires 
projectiles at enemies located above. Left and right movement is performed either with arrow keys or WASD. Each press of
the space bar launches a projectile, though the number of projectiles allowed at once are limited. 

## Current State

Core gameplay has been implemented, but the game loops has not been completed. 

While the game can work in multiple sizes/resolutions, more solutions must be implemented before it will be able to swap
between sizes on the fly.

## todo

make entity speed scale at different resolutions

move player object from stage to game or elsewhere

add enemy collision and player health loss

implement victory and defeat scenarios

introduce more stages and more enemy types

implement proper pre-game set up and post-game/post-return-to-menu resets

create settings menu with sound options and screen resizing