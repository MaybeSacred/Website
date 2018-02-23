module AllLinks
open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System

let ``all-programming-links`` = {
    Title = "All Programming Links"
    Modified = DateTime.Now
    Content = Nodes (fun () -> List.ofSeq <| seq {
        yield p [] [rawText "This is a set of useful, interesting, cultivated links related to programming. Topics include programming language design, functional programming, and software development"]
        yield! renderLinks programmingLinks 
    })
    }

let ``all-fun-links`` = {
    Title = "All Fun Links"
    Modified = DateTime.Now
    Content = Nodes (fun () ->
        List.ofSeq <| seq {
            yield p [] [rawText "All the weird little corners of the internet"]
            yield! renderLinks funLinks 
    } )}

let sitemap = {
    Title = "Site Map"
    Modified = DateTime.Now
    Content = Nodes (fun () ->
        List.ofSeq <| seq {
            yield p [] [rawText "All portions of my website"]
            yield! renderLinks mainLinks 
    })}