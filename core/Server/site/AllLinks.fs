module AllLinks
open CommonHtml
open Suave.FunctionalViewEngine

let ``all-programming-links`` () =
    seq {
        yield p [] [rawText "This is a set of useful, interesting, cultivated links related to programming. Topics include programming language design, functional programming, and software development"]
        yield! renderLinks programmingLinks 
    }
    |> List.ofSeq
    |> template "All Programming Links"

let ``all-fun-links`` () =
    seq {
        yield p [] [rawText "All the weird little corners of the internet"]
        yield! renderLinks funLinks 
    }
    |> List.ofSeq
    |> template "All Fun Links"

let sitemap () =
    seq {
        yield p [] [rawText "All portions of my website"]
        yield! renderLinks mainLinks 
    }
    |> List.ofSeq
    |> template "Site Map"