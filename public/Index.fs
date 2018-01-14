module Index
open CommonHtml
open Suave.FunctionalViewEngine

let page =
    template "Main Page" [
        rawText "Welcome to Jon's awesome website!"
    ]
