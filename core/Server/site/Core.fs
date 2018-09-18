module Core
open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System

let page = {
    Title = "Home"
    Created = DateTime.Now
    Modified = DateTime(2018,2,22)
    Content = Nodes (fun () ->
    [
        paragraph "Welcome to my totes awesomesauce website!"
        paragraph "Have a look around!"
    ] )}

let ``404`` = {
    Title = """4O4 pAgE N0t foUnD"""
    Created = DateTime(2018,2,22)
    Modified = DateTime(2018,2,22)
    Content = Nodes (fun () ->
    [
        div [class' "text-center"] [
            h3 [] [rawText "Uh oh! Looks like that page doesn't exist"]
            img [attr "src" "https://http.cat/404"; class' "mw-25"]
        ]
    ] )}

let ``dev\random`` = {
    Title = """\dev\random\"""
    Created = DateTime.Now
    Modified = DateTime(2018,2,22)
    Content = Nodes (fun () ->
    [
        div [class' "align-middle"] [
            a [attr "href" """https://xkcd.com/221/"""] [
                img [attr "src" "https://imgs.xkcd.com/comics/random_number.png"]
            ]
        ]
    ] )}
