The Command Line Murders
========================

	.OOOOOOOOOOOOOOO @@                                   @@ OOOOOOOOOOOOOOOO.
	OOOOOOOOOOOOOOOO @@                                    @@ OOOOOOOOOOOOOOOO
	OOOOOOOOOO'''''' @@                                    @@ ```````OOOOOOOOO
	OOOOO'' aaa@@@@@@@@@@@@@@@@@@@@"""                   """""""""@@aaaa `OOOO
	OOOOO,""""@@@@@@@@@@@@@@""""                                     a@"" OOOA
	OOOOOOOOOoooooo,                                            |OOoooooOOOOOS
	OOOOOOOOOOOOOOOOo,                                          |OOOOOOOOOOOOC
	OOOOOOOOOOOOOOOOOO                                         ,|OOOOOOOOOOOOI
	OOOOOOOOOOOOOOOOOO @          THE                          |OOOOOOOOOOOOOI
	OOOOOOOOOOOOOOOOO'@           COMMAND                      OOOOOOOOOOOOOOb
	OOOOOOOOOOOOOOO'a'            LINE                         |OOOOOOOOOOOOOy
	OOOOOOOOOOOOOO''              MURDERS                      aa`OOOOOOOOOOOP
	OOOOOOOOOOOOOOb,..                                          `@aa``OOOOOOOh
	OOOOOOOOOOOOOOOOOOo                                           `@@@aa OOOOo
	OOOOOOOOOOOOOOOOOOO|                                             @@@ OOOOe
	OOOOOOOOOOOOOOOOOOO@                               aaaaaaa       @@',OOOOn
	OOOOOOOOOOOOOOOOOOO@                        aaa@@@@@@@@""        @@ OOOOOi
	OOOOOOOOOO~~ aaaaaa"a                 aaa@@@@@@@@@@""            @@ OOOOOx
	OOOOOO aaaa@"""""""" ""            @@@@@@@@@@@@""               @@@|`OOOO'
	OOOOOOOo`@@a                  aa@@  @@@@@@@""         a@        @@@@ OOOO9
	OOOOOOO'  `@@a               @@a@@   @@""           a@@   a     |@@@ OOOO3
	`OOOO'       `@    aa@@       aaa"""          @a        a@     a@@@',OOOO'


There's been a murder in Terminal City, and TCPD needs your help.

To figure out whodunit, you need access to a command line.

Once you're ready, clone this repo, or [download it as a zip file](https://github.com/veltman/clmystery/archive/master.zip).

Open a Terminal, go to the location of the files, and launch the game:

	python3 game.py

The game opens a guided, shell-like prompt with commands such as `ls`, `cd`,
`cat`, `grep`, `awk`, `head`, `tail`, and `wc`. Use `hint` for a clue,
`check NAME` to check an answer, `solution` to reveal it, and `cheatsheet` for
a built-in command reference. Press Tab to complete commands and case-file
paths.

After a correct answer, the game displays the successfully executed commands
and the elapsed time in minutes.

Colors are enabled automatically in supported interactive terminals. Use
`python3 game.py --color always` or `python3 game.py --color never` to override
automatic detection.

The assigned mystery is saved between launches so a player can resume the same
case. To switch cases while testing locally, run `python3 game.py --new-case`.

The prompt intentionally supports only a subset of a real shell; it does not
run arbitrary operating-system commands or support file-writing redirection.
The files are still present in a local clone, so this is a guided game
interface rather than a security boundary. Do not use a text editor to inspect
the case files if you want to solve the mystery as intended.

Use the in-game `cheatsheet` command while playing. For command-line practice
outside the game, see cheatsheet.md or cheatsheet.pdf.

### Credits

By Noah Veltman  
Projects: [noahveltman.com](http://noahveltman.com)  
GitHub: [veltman](https://github.com/veltman)  
Twitter: [@veltman](https://twitter.com/veltman)  
