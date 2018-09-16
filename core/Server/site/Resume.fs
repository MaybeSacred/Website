module Resume

open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System
let content = [
    div [class' "container"] [
        div [class' "row mt-2"] [
            div [class' "col"] [
                h1 [class' "text-center"] [rawText "Jonathan Tyson"]
                h6 [class' "text-center"] [rawText "jtyson79473@gmail.com"]
                h6 [class' "text-center"] [anchor "github.com/MaybeSacred" "https://github.com/MaybeSacred"]
                h6 [class' "text-center"] [anchor "tysonontech.sytes.net" "http://tysonontech.sytes.net"]
            ]
        ]
        div [class' "row mt-3"] [
            div [class' "col-12"] [
                h3 [class' "text-center"] [rawText "Professional Experience"]
            ]
            div [class' "col-12 col-sm-6 text-center text-sm-left"] [
                h6 [class' "text-bold mb-0"] [rawText "NextGen Healthcare"]
                em [class' "text-muted"] [rawText "Buckhead, GA"]
            ]
            div [class' "col-12 col-sm-6 text-center text-sm-right"] [
                h6 [class' "text-bold mb-0"] [rawText "Software Engineer and Intern"]
                em [class' "text-muted"] [rawText "3/2015-9/2018"]
            ]
            div [class' "col"] [
                ul [] [
                    li [] [rawText "Work across a variety of technology stacks and systems, including C# and VB.NET back-ends, ASP.NET, Javascript, Telerik, and jQuery front-ends; MySQL and TSQL; JSON, XML, CSV and flat files; AIX and Windows Server; Powershell, Python, and Perl"]
                    li [] [rawText "Independently develop many lightweight WinForms and WPF utilities that provide features or bug workarounds for clients"]
                    li [] [rawText "Write unit and integration tests, documentation, and deployment and automation scripts"]
                    li [] [rawText "Adeptly balance feature requests and bug fixes with system, code, and process improvements"]
                    li [] [rawText "Mentor fellow coworkers and encourage the adoption of skills like logging, library usage, concurrency, functional programming, and build and deployment automation"]
                ]
                h5 [class' "text-center"] [rawText "Accomplishments"]
                ul [] [
                    li [] [rawText "Refactored a bug- and race-condition riddled program that ran other programs into a streamlined highly-concurrent fault-tolerant application runner while halving the LOC count and greatly reducing issues"]
                    li [] [rawText "Combined seven programs with high defect rates that together formed a single business process handling $220k a month into two performant programs that have not had an error or failure in over one year"]
                    li [] [rawText "Championed the addition of open-source libraries like Dapper, moment.js, and Nlog"]
                ]
            ]
        ]
        hr []
        div [class' "row"] [
            div [class' "col-12 col-sm-6 text-center text-sm-left"] [
                h6 [class' "text-bold mb-0"] [rawText "Club Scientific Summer Camp"]
                em [class' "text-muted"] [rawText "Atlanta, GA"]
            ]
            div [class' "col-12 col-sm-6 text-center text-sm-right"] [
                h6 [class' "text-bold mb-0"] [rawText "Camp Staff"]
                em [class' "text-muted"] [rawText "6/2013-8/2013"]
            ]
            div [class' "col"] [
                ul [] [li [] [rawText "Taught a science-based curriculum including video game development to kids ages 4-14"]]
            ]
        ]
        div [class' "row mt-3"] [
            div [class' "col text-center"] [
                h3 [] [rawText "Education"]
                p [] [
                    rawText """Senior at Georgia Institute of Technology, Computer Science"""
                    br []
                    rawText """Southern Polytechnic State University, Computer Science"""
                ]
            ]
        ]
        div [class' "row mt-3"] [
            div [class' "col text-center"] [
                h3 [] [rawText "Languages"]
                p [] [rawText """F#, Typescript, C# (98th percentile in Pluralsight), Javascript, Haskell, Powershell, (My|T|Postgre)SQL, Python,  CSS, HTML"""]
            ]
        ]
        div [class' "row mt-3"] [
            div [class' "col text-center"] [
                h3 [] [rawText "Technologies"]
                p [] [rawText """Windows, Linux, Webpack, MSBuild, IIS, React, Sass, Bootstrap, ASP.NET, .NET Core, jQuery"""]
            ]
        ]
        div [class' "row mt-3"] [
            div [class' "col text-center"] [
                h3 [] [rawText "Skills"]
                p [] [rawText """Database Management and Design, Debugging in Chrome/Firefox/IE, Database and Code Performance Tuning, Security Best Practices, ReactiveX, Parallel and Asynchronous Programming"""]
            ]
        ]
        div [class' "row mt-3"] [
            div [class' "col text-center"] [
                h3 [] [rawText "Inspiration"]
                p [] [rawText """Coding Horror, Joel Spolsky, The Daily WTF, Mythical Man-Month, C# in Depth, F# for Fun and Profit, Advanced Windowing Functions in T-SQL"""]
            ]
        ]
        // TODO: add links for various things
        div [class' "row mt-3"] [
            div [class' "col text-center"] [
                a [href "Resume.pdf"; title' "Resume"; flag "download"] [rawText "Download as PDF"]
            ]
        ]
    ]
]
let page = {
    Title = "Resume" 
    Created = DateTime(2018, 9, 11)
    Modified = DateTime.Now
    Content = textify content }
