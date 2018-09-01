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
    [// have these sections alternate on sides of the page, with title and text on one side, graphic on other
        div [class' "container"] [
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    h3 [class' "text-center"] [rawText "About Me"]
                    p [class' "text-center align-middle"] [
                        sprintf """Hi, my name is Jon Tyson. I'm %i years old and live in 
                        Atlanta, Georgia. I have a dog named Bronx and cute girlfriend Caroline. 
                        I enjoy long walks on the beach, long hikes in 
                        the forest, and short download times. I am currently working as a 
                        full-stack software engineer at """ (yearsOld <| DateTime(1990,10,26)) |> rawText 
                        anchor "NextGen Healthcare" """https://www.nextgen.com/"""
                        rawText """, a healthcare IT company. In my free time, I'm usually programming for fun, exercising, reading books, or watching Netflix."""
                    ]
                ]
                div [class' "col-12 col-sm-6"] [img [src "bronx.png"; class' "img-fluid mx-auto d-block"]]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    a [href "http://lambda-the-ultimate.org/"; title' "Haskell Logo"] [img [src "haskell_logo.svg"; class' "img-fluid mx-auto d-block"; attr "width" "406"]]
                ]
                div [class' "col-12 col-sm-6"] [
                    h3 [class' "text-center"] [rawText "About this Site"]
                    p [class' "text-center align-middle"] [
                        rawText """I created this site to blog about and explore technologies. The core site is 
                        written in """
                        anchor "F#" """http://fsharp.org/"""
                        rawText """, a statically-typed functional-first programming language. Styling is done primarily with """
                        anchor "Bootstrap" """https://getbootstrap.com/"""
                        rawText """, giving it that 'fresh from 2017' look-and-feel everyone loves. Other components of the site will 
                        be built out over time with different technologies and documented through a series of articles."""
                    ]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    h3 [class' "text-center"] [rawText "Things I Like"]
                    rawText "Favorite bash Command"
                    br []
                    code [] [rawText "dd if=/dev/random of=/dev/sda"]
                ]
                div [class' "col-12 col-sm-6"] []
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [img [src "https://i.redd.it/8z55tyc7t8j11.jpg"; class' "img-fluid mx-auto d-block"; attr "width" "406"]]
                div [class' "col-12 col-sm-6"] [
                    h3 [class' "text-center"] [rawText "Favorite SubReddits"]
                    anchor "r/ProgrammerHumor" """https://www.reddit.com/r/ProgrammerHumor"""
                    rawText " and "
                    anchor "r/aww" """https://www.reddit.com/r/aww/"""
                ]
            ] // favorite movie
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    h3 [class' "text-center"] [rawText "Favorite Animal-Themed TV Show"]
                    anchor "Bojack Horseman" """https://www.netflix.com/title/70300800"""
                    // arrested development
                ]
                div [class' "col-12 col-sm-6"] [
                    img [src "bojack.jpg"; attr "height" "360"; attr "width" "360" ]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    iframe [attr "width" "480"; attr "height" "270"; src """https://www.youtube.com/embed/rId6PKlDXeU"""] []
                ]
                div [class' "col-12 col-sm-6"] [
                    a [href """https://www.mumfordandsons.com/"""; title' "Mumford and Sons"] [h3 [class' "text-center"] [rawText "Mumford and Sons"]]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    anchor "Julien Baker" """https://julienbaker.com/"""
                ]
                div [class' "col-12 col-sm-6"] [
                    iframe [attr "width" "480"; attr "height" "270"; src """https://www.youtube.com/embed/XZdnq5tN5vI"""] []
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    iframe [attr "width" "480"; attr "height" "270"; src """https://www.youtube.com/embed/dyQJH615KwA"""] []
                ]
                div [class' "col-12 col-sm-6"] [
                    anchor "Buckethead" """https://www.youtube.com/watch?v=tADWPTqR_4A"""
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-sm-6"] [
                    // https://www.ballastpoint.com/beer/aloha-sculpin/
                    // brewery- ballast point, include pic
                    // favorite vidya game pokemon?
                ]
            ]
        ]
    ])}
