# A very much not real-time renderer, written in python, made to render the olympic rings.
This is a project that I have been wanting to do for a while, and the competition was all the excuse I needed. The main inspirations to do this have been Acerola (https://www.youtube.com/@Acerola_t) and Sebastian Lague's episode on ray tracing (https://www.youtube.com/watch?v=Qz0KTGYJtUk).

Although they both have inspired me and given me quite some background knowledge, most concrete concepts I took not from them but from the book <i>Computer Graphics from Scratch: A Programmer's Introduction to 3D Rendering</i> (ISBN-13 978-1718500761), by Gabriel Gambetta.

The <i>mess.txt, mess-parser.py, out.txt, mess-out-parser.py, end.txt</i> and <i>quartlib.py</i> files are all related to solving a quartic equation for the intersection of a line and a torus (for the olympic rings). They contain some more info, but the gist is that it should work but doesn't, and I spent a lot of time working on that that could have been used to improve other parts of the program.

I originally did not read the competition regulations fully, and started of using the numba cuda library to interface with the gpu and get this running faster. I later realised this and started again, but the time wasted there is probably similar to the extra time necessary to get stuff working on the gpu (that's a pain). 

I'm quite sad my implementation of the torus didn't work out, because that was the bit of code has been done already by the lowest number of people, and it's also the challenge I enjoyed the most until I had verified that all things were as they should be exept the fact that it doesn't work. When testing with a torus at (5, 0, 0) with major radius 2 and minor radius 1, and a ray from (0, 2, 0) with direction (1, 0, 0), it spits out a polynomial which it solves correctly to four imaginary roots. It should be a polynomial with the two real roots 4 and 6, and two imaginary roots. But, as I explain in the docstring in the relevant file, it doesn't work and it should work.

This project can be found online at https://github.com/ianic-dev/Render_olympics

## Code explanation

The main thing necessary to understand the code is the data structure I use for a ray. It's a numpy.ndarray of shape (2, 3), interpreted as one vector to the origin of the ray and one unit vector as the direction. So ray[0] is the camera, and then the bouncepoint for bounced light, and ray[1] is the direction the light is going. 

<i>lib.py</i> contains the classes made for this project, with the names hopefully being self-explanatory. I designed the sphere and torus classes to be mostly indistinguishable as far as methods go, but as I said the torus is broken. The light class is only used for the approach with <i>trace = False</i>, and can be either ambient, directional or a point.

<i>tracefuncs.py</i> contains the bulk of the rendering code. I hope that the docstrings and comments in the functions there will be suficcient to understand the code, and the book is very much recommended if you actually want to learn how rendering works.

<i>main.py</i> has the code for the scene setup and the cli (command line interface), except for the progress bar which is in the <i>dispatched</i> function. I copied the progress bar  from the Arch Linux package manager, pacman. I know that the continue/break/loop=False stuff is a mess, but it's currently 4:20 in the morning and i'm 

The <i>multiprocessing</i> module is used to parallelise a bit, but you're still doing GPU work on the CPU. This program is not fast. 12 processes are created, but it will not be around 1/12 of the time of a single-threaded version, unless your processor has at least 12 cores. Python also has a module called threading, which does not work for parallel processing due to limitations of the python interpreter. Each process gets assigned a queue (which could have been a pipe if I spent the time learning about those), which it uses to return data to the parent process. I have also tested this program on my laptop running Linux with an Intel i7-10750H, and most non-extreme settings run in reasonable time.

### Usage guide

"q" or "quit" at any input will exit the program, and more features become available each iteration of the render loop. After the third iteration, all parameters are available and a final showoff render is recommended. I recommend running the program from an actual terminal, to get the best experience. Running <i>python main.py</i> in the vscode/pycharm terminal is what I do.

The default camera looks in the positive x direction, with positive y being up and positive z being right. Scene 3 is essentially made for playing around with rotation on the Y axis, and for most of the scenes you'll find a sun-like light source above you (use z rotation to look up). I would strongly recommend trying out some camera positions and rotations to explore scene 3.

The parameters recommended for a final showoff render are: scene 2, resolution of 360x360, 256 rays per pixel, depth of 6. If you have way too much time you can use 512 or higher at 720x720 and go do something else while it renders. The png is from when I rendered that, and it took about an hour. The progress bar shows process 5 as that handles pixels closer to the centre of the screen, which tend to take longer as there is more stuff there. Scene 2 is supposed to be the olympic rings, if it wasn't obvious. They would definitely be better as actual rings.

## Conclusion

Well, here it is. My first actual coding project. I've got some ideas lined up for future free time, mostly learning C, interfacing with API's and building a tui. I'll probably come back to this project in the future, but I will definitely be running a statically typed language. You'll probably have guessed that I was dead set on doing this the moment I heard about the competition, and the olympics part was shoehorned in later. Although it didn't work out in the end, I did enjoy playing with tori. You can insert "Torus(0.5, 2, np.array([1, 0, 0]), np.array([9, -.5, 2]), np.array([30, 140, 200]), 10, 0)" at (65, 16) in <i>main.py</i> to see something broken. It tends to just not show, but I think you can probably spot something off.