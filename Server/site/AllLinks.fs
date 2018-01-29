module AllLinks
open CommonHtml
open Suave.FunctionalViewEngine

let ``all-programming-links`` () =
    seq {
        yield p [] [rawText "This is a set of useful, interesting, or blah links related to programming. Topics include programming language design, functional programming, and development"]
        yield! renderLinks programmingLinks 
    }
    |> List.ofSeq
    |> template "All Programming Links"

let ``all-fun-links`` () =
    seq {
        yield p [] [rawText "Funny-ass shit"]
        yield! renderLinks funLinks 
    }
    |> List.ofSeq
    |> template "All Programming Links"