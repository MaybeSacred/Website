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
            sprintf """Hi! My name is Jon Tyson. I'm %i years young and currently live in 
            Atlanta, Georgia. I have a dog named Bronx and enjoy long walks on the beach, long hikes in 
            the forest, and short download times. I am currently working as a 
            full-stack software engineer at """ (yearsOld <| DateTime(1990,10,26)) |> rawText 
            anchor "NextGen Healthcare" """https://www.nextgen.com/"""
            rawText """, a healthcare IT company. In my free time, I'm usually programming for fun, reading books, or watching Netflix."""
        ]
        h3 [] [rawText "About this Site"]
        p [] [
            rawText """I created this site to blog about and explore technologies. The core site is 
            written in """
            anchor "F#" """http://fsharp.org/"""
            rawText """, a statically-typed functional-first programming language. Styling is done primarily with """
            anchor "Bootstrap" """https://getbootstrap.com/"""
            rawText """, giving it that 'fresh from 2017' look-and-feel everyone loves. Other components of the site will 
            be built out over time with different technologies and documented through a series of articles."""
        ]
        h3 [] [rawText "Factoids"]
        ul [class' "list-unstyled"] [
            // include pictures of these things
            li [] [
                rawText "Favorite bash Command: "
                code [] [rawText "dd if=/dev/random of=/dev/sda"]
            ]
            li [] [
                rawText "Favorite SubReddits: "
                anchor "r/ProgrammerHumor" """https://www.reddit.com/r/ProgrammerHumor"""
                rawText " and "
                anchor "r/aww" """https://www.reddit.com/r/aww/"""
            ]
            li [] [
                rawText "Favorite Animal-Themed TV Show: "
                anchor "Bojack Horseman" """https://www.netflix.com/title/70300800"""
            ]
            li [] [
                // music
            ]
            li [] [
                // programming lang
            ]
            li [] [
                // brewery- ballast point, include pic
            ]
        ]
        // r/aww and r/programmerhumour
        // bojack horseman
        // 
        br []
    ])}
