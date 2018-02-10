module Index
open CommonHtml
open Suave.FunctionalViewEngine

let page () =
    template "Home" [
        rawText "Welcome to my totes awesomesauce website!"
        rawText "Have a look around"
    ]

let ``dev\random`` () = 
    template """\dev\random\""" [
        img [attr "src" @"https://imgs.xkcd.com/comics/random_number.png"]
        a [attr "href" """https://xkcd.com/221/"""] [rawText "Source"]
    ]
