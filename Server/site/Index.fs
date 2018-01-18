module Index
open CommonHtml
open Suave.FunctionalViewEngine

let page () =
    template "Main Page" [
        rawText "Welcome to Jon Tyson's awesome website!"
    ]

let ``dev\random`` () = 
    template """\dev\random\""" [
        img [attr "src" @"https://imgs.xkcd.com/comics/random_number.png"]
        a [attr "href" """https://xkcd.com/221/"""] [rawText "Source"]
    ]