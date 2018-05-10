module About
open CommonHtml
open Suave.FunctionalViewEngine
open System
open Types

let yearsOld (bDate:DateTime) = 
    let today = DateTime.Today
    let age = today.Year - bDate.Year
    if bDate > today.AddYears -age then age - 1 else age
let about = {
    Title = "About" 
    Created = DateTime.Now
    Modified = DateTime.Now
    Content = Nodes (fun () ->
    [
        h2 [class' "text-center"] [rawText "Welcome to my Personal Site"]
        br []
        h3 [] [rawText "About Me"]
        p [] [
            sprintf """Hi! My name is Jon Tyson and I created this website. I'm %i years young and I'm a software developer currently living in 
            Atlanta, Georgia. I have a dog named Bronx and I enjoy long walks on the beach, long hikes in 
            the forest, and long download times. Just kidding about the last one. I currently work as a 
            full-stack software engineer at """ (yearsOld <| DateTime(1990,10,26)) |> rawText 
            anchor "NextGen Healthcare" """https://www.nextgen.com/"""
            rawText """, a health care IT company. In my free time, I'm usually programming for fun, reading books, or watching Netflix"""
        ]
        p [] [
            rawText "Favorite bash Command: "
            code [] [rawText "dd if=/dev/random of=/dev/sda"]
        ]
        br []
        h3 [] [rawText "About this Site"]
        p [] [
            rawText """This is a site where I can blog, vblog, blag, brag, and generally have fun. The core site is 
            written in """
            anchor "F#" """http://fsharp.org/"""
            rawText """, a statically-typed functional-first programming language. Other components of the site will 
            be built out over time with different technologies and documented through a series of haaaunted articles """
            anchor "starting here" """"""
        ]
    ])}
