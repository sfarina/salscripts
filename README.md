# salscripts
just some things that I made that I found useful

## diskreport.py
a wrapper for du. POSIX only.
ex:
```
$ diskreport.py -i 0.1 -t 0.1
  369.5 M ./lib
          130.2 M ./lib/modules
          109.6 M ./lib/locale
                  107.8 M ./lib/locale/locale-archive
  369.0 M ./share
          104.3 M ./share/locale
  208.2 M ./lib64
  137.4 M ./bin
```

