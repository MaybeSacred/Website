module Index
open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System

let page = {
    Title = "Home"
    Modified = DateTime(2018,2,22)
    Content = Nodes (fun () ->
    [
        paragraph "Welcome to my totes awesomesauce website!"
        paragraph "Have a look around!"
    ] )}

let ``dev\random`` = {
    Title = """\dev\random\"""
    Modified = DateTime(2018,2,22)
    Content =Nodes (fun () ->
    [
        div [class' "align-middle"] [
            a [attr "href" """https://xkcd.com/221/"""] [
                img [attr "src" @"https://imgs.xkcd.com/comics/random_number.png"]
            ]
        ]
    ] )}
