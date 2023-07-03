# Benndot's Arcade Shooter 2.0

An attempt at making a two-dimensional arcade-style shooting game. 

## Game Overview

The gameplay is that of a classic 2D vertical shooter, where the player moves back and forth on the x-axis and fires 
projectiles at enemies located above. Left and right movement is performed either with arrow keys or WASD. Each press of
the space bar launches a projectile, though the number of projectiles allowed at once are limited. 

The game's setting is a cartoon-ish depiction of the 1960's. The plot scenario is of a stereotypical suburban dad facing
off against a group of hippies, armed with nothing but a sport bag full of baseballs. 

## Gameplay

The core gameplay, as well as the basic game loop has been implemented. The player can move and shoot mostly as 
intended. Enemies are generated with randomized positions and movement directions, they can be shot with projectiles, 
and in one case, can shoot their own. 

A collision system is in place to capture any contact that results from this gameplay; enemies have health and will lose 
1 point of health if hit by a projectile. The player, if contacted by an enemy projectile or low-moving enemy, will
automatically lose. 

A UI spanning the left and right margins of the display show the current stage and the number of enemies remaining.

Defeating every enemy reveals a win screen. A stage will be flagged as complete if it wasn't already. A "continue" 
button will appear that allows the player to return to the main menu. Upon continuing, all necessary game resets will be 
made so that subsequents rounds will play out properly. 

The defeat scenario reveals a loss screen with a similar setup to the winning screen that allows the user to return to 
the start menu and perform all necessary game resets. 

Three game stages currently exist, with differing names and selection/quantities of enemies.

## Other features

The game allows for resolution to be swapped via a menu made for that purpose. This is the first screen that appears 
when the program is started, and can also be returned to from the settings menu. 

The start menu is the game's main hub. From there, the user can select which level to play, start the game or go off 
into the settings menu. 

The settings menu is accessible from the start menu and allows the user to change the sound effect volume. It also 
allows the user to return to the resolution changing screen. 

The game has a multiple song soundtrack, with the menu and each level having their own tracks that swap and fade-in or 
out as screens transition between each other. Victory and defeat screens also have their own jingles. Sound effects are
implemented into the gameplay, primarily used to indicate collisions and button clicks. 

## Controls

Movement: WASD or Arrow Keys

Shoot: Space

Return to menu: Esc

Mute music: M (in-game only)

## todo

iterate through enemy details dict in order to list of their health and images in the right margin

move player object out of stage class and into game class

turn player projectile limit into a time-based cooldown

in-game gif effects? Locked stages? Different kinds of projectiles?

## Issues

Why is it harder to click the continue button that appears after a game round has ended? 