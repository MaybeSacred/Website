module Index
open CommonHtml
open Suave.FunctionalViewEngine

let page () =
    template "Home" [
        paragraph "Welcome to my totes awesomesauce website!"
        paragraph "Have a look around!"
    ]

let ``dev\random`` () = 
    template """\dev\random\""" [
        div [class' "align-middle"] [
            a [attr "href" """https://xkcd.com/221/"""] [
                img [attr "src" @"https://imgs.xkcd.com/comics/random_number.png"]
            ]
        ]
    ]
