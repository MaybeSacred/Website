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
        div [class' "container"] [
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
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
                div [class' "col-12 col-m-6"] [img [src "bronx.png"; class' "img-fluid mx-auto d-block"]]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    a [href "http://lambda-the-ultimate.org/"; title' "Haskell Logo"] [img [src "haskell_logo.svg"; class' "img-fluid mx-auto d-block"; attr "width" "406"]]
                ]
                div [class' "col-12 col-m-6"] [
                    h3 [class' "text-center"] [rawText "About this Site"]
                    p [class' "text-center align-middle"] [
                        rawText """I created this site to blog about and explore technologies. The core site is written in """
                        anchor "F#" """http://fsharp.org/"""
                        rawText """, a statically-typed functional-first programming language. Styling is done primarily with """
                        anchor "Bootstrap" """https://getbootstrap.com/"""
                        rawText """, giving it that 'fresh from 2017' look-and-feel everyone loves. Other components of the site will 
                        be built out over time with different technologies and documented through a series of articles."""
                    ]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    h3 [class' "text-center"] [rawText "Things I Like"]
                ]
                div [class' "col-12 col-m-6"] [img [src "pink-floyd-dark-side-of-the-moon.jpg"; class' "img-fluid mx-auto d-block"; attr "width" "510"; title' "Pink Floyd - Dark Side of the Moon"]]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [img [src "https://i.redd.it/8z55tyc7t8j11.jpg"; class' "img-fluid mx-auto d-block"; attr "width" "480"]]
                div [class' "col-12 col-m-6"] [
                    h3 [class' "text-center"] [anchor "r/ProgrammerHumor" """https://www.reddit.com/r/ProgrammerHumor"""]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    h3 [class' "text-center"] [anchor "r/ItemShop" """https://www.reddit.com/r/ItemShop/"""]
                ]
                div [class' "col-12 col-m-6"] [img [src "https://i.redd.it/ko7o1xut8ak11.jpg"; class' "img-fluid mx-auto d-block"; attr "width" "400"]]
            ]
            // favorite movie
            // arrested development
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    img [src "bojack.jpg"; class' "img-fluid mx-auto d-block"; attr "height" "300"; attr "width" "300" ]
                ]
                div [class' "col-12 col-m-6"] [
                    h3 [class' "text-center"] [anchor "Bojack Horseman" """https://www.netflix.com/title/70300800"""]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    a [href """https://www.mumfordandsons.com/"""; title' "Mumford and Sons"] [h3 [class' "text-center"] [rawText "Mumford and Sons"]]
                ]
                div [class' "col-12 col-m-6 d-flex justify-content-center"] [
                    iframe [attr "width" "480"; attr "height" "270"; src """https://www.youtube.com/embed/rId6PKlDXeU"""] []
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6 d-flex justify-content-center"] [
                    img [src "https://cdn.bulbagarden.net/upload/e/e3/145Zapdos.png"; class' "img-fluid mx-auto d-block"; attr "width" "300"; title' "Zapdos Pokemon"]
                ]
                div [class' "col-12 col-m-6"] [
                    a [href """https://bulbapedia.bulbagarden.net/wiki/Stufful_(Pok%C3%A9mon)"""; title' "Pokemon (Stufful)"] [h3 [class' "text-center"] [rawText "Pokémon"]]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    a [href """https://julienbaker.com/"""; title' "Julien Baker"] [h3 [class' "text-center"] [rawText "Julien Baker"]]
                ]
                div [class' "col-12 col-m-6 d-flex justify-content-center"] [
                    iframe [attr "width" "480"; attr "height" "270"; src """https://www.youtube.com/embed/XZdnq5tN5vI"""] []
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6 d-flex justify-content-center"] [
                    img [src "V-emblem_32.png"; class' "img-fluid mx-auto d-block"; attr "width" "240"; title' "Eliwood and a Divine Dragon"]
                ]
                div [class' "col-12 col-m-6"] [
                    a [href """http://fireemblem.wikia.com/wiki/Lyndis"""; title' "Fire Emblem (Lyndis)"] [h3 [class' "text-center"] [rawText "Fire Emblem"]]
                ]
            ]
            div [class' "row align-items-center"] [
                div [class' "col-12 col-m-6"] [
                    a [href """https://fatherjohnmisty.com/"""; title' "Father John Misty"] [h3 [class' "text-center"] [rawText "Father John Misty"]]
                ]
                div [class' "col-12 col-m-6 d-flex justify-content-center"] [
                    iframe [attr "width" "480"; attr "height" "270"; src """https://www.youtube.com/embed/ga0ksTIagsg"""] []
                ]
            ]
        ]
    ])}
