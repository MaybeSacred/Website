module About
open CommonHtml
open Suave.FunctionalViewEngine

let about () =
    template "About" [
        h2 [class' "text-center"] [rawText "Welcome to my Personal Site"]
        br []
        h3 [] [rawText "About Me"]
        rawText """Hi!
        My name is Jon Tyson and I created this website. I'm a software developer currently living in 
        Atlanta, Georgia. I have a dog named Bronx and I enjoy long walks on the beach, long hikes in 
        the forest, and long download times. Just kidding about the last one. I currently work as a 
        full-stack software engineer at """
        anchor "NextGen" """https://www.nextgen.com/"""
        rawText """, a health care IT company. In my free time, I'm usually programming for fun, reading nifty novels, or chilling watching Netflix"""
        br []
        br []
        h3 [] [rawText "About this Site"]
        rawText """This is a site where I can blog, vblog, blag, brag, and generally have fun. The site is a 
        constant work in progress and provides a chance to leverage different technologies. The core site is 
        written in """
        anchor "F#" """http://fsharp.org/"""
        rawText """, a statically-typed functional-first programming language."""
    ]
