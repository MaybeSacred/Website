module Resume
open CommonHtml
open Suave.FunctionalViewEngine

let page =
    template "Resume" [
        // move these to a side bar, make them random and only show two or three at a time
        // have a testimonials section here
        p [] [rawText "Jon Tyson is awesomesauce! You should hire him for any software engineering that is not Java development! - Every Software Engineer"]
        p [] [rawText "Jon feed Bronx and walk Bronx every day and love Bronx. Jon good boy, very good boy like Bronx - Bronx, Jon's dog"]
        p [] [rawText "It's 2AM! Turn off the %*&#%@ jazz! - Downstairs Neighbor"]
        p [] [rawText "Cowabunga! - Bart Simpson"]
    ]
