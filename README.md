### Battleship

A 1-player (player vs. computer) version of the game Battleship, implemented with Pygame and pygame_gui.

- computer's ships are placed randomly
- player can place ships manually
- player always goes first
- computer guesses squares randomly (can even guess a previously guessed square)


Bonus features:

- button to randomize ship placements for player
- buttons to adjust & confirm ship placements
- new game button
- improve the bot/AI intelligence (from just guessing randomly)


Questions:
- sample random placements of ships: with what probability are certain squares occupied?
    - does this change if the ships are placed in a different order (e.g. largest first vs. smallest first?)
- what's the best guessing pattern to locate any of the remaining ships efficiently? (once you sink the smallest ship, it's easier to find the other ships since they're bigger, but it's on average harder to find the smallest ship)