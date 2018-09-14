module Resume

open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System
let content = [
    div [class' "container"] [
        h3 [class' "text-center display-4"] [rawText "Jonathan Tyson"]
        h6 [class' "text-center"] [rawText "jtyson79473@gmail.com"]
        h6 [class' "text-center"] [anchor "github.com/MaybeSacred" "https://github.com/MaybeSacred"]
        h6 [class' "text-center"] [anchor "tysonontech.sytes.net" "http://tysonontech.sytes.net"]
        h3 [class' "text-center"] [rawText "Professional Experience"]
        hr []
        div [class' "row"] [
            div [class' "col-12 col-sm-6"] [
                strong [class' "text-bold"] [rawText "NextGen Healthcare"]
                br []
                em [class' "text-muted"] [rawText "Buckhead, GA"]
            ]
            div [class' "col-12 col-sm-6"] [
                p [class' "text-right"] [
                    strong [class' "text-bold text-right"] [rawText "Software Engineer and Intern"]
                    br []
                    em [class' "text-muted text-right"] [rawText "3/2015-9/2018"]
                ]
            ]
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
        hr []
        div [class' "row"] [
            div [class' "col-12 col-sm-6"] [
                span [class' "text-bold"] [rawText "Club Scientific Summer Camp"]
                br []
                span [class' "text-italic"] [rawText "Atlanta, GA"]
            ]
            div [class' "col-12 col-sm-6"] [
                span [class' "text-bold"] [rawText "Camp Staff"]
                br []
                span [class' "text-italic"] [rawText "6/2013-8/2013"]
            ]
        ]
        p [] [rawText "Taught a science-based curriculum including video game development to kids ages 4-14"]
        h3 [class' "text-center"] [rawText "Education"]
        div [class' "row"] [p [] [rawText """Senior at Georgia Institute of Technology, Computer Science"""]]
        div [class' "row"] [p [] [rawText """Southern Polytechnic State University, Computer Science"""]]
        h3 [class' "text-center"] [rawText "Languages"]
        p [] [rawText """F#, Typescript, C# (98th percentile in Pluralsight), Javascript, Haskell, Powershell, (My|T|Postgre)SQL, Python,  CSS, HTML"""]
        h3 [class' "text-center"] [rawText "Technologies"]
        p [] [rawText """Windows, Linux, Webpack, MSBuild, IIS, React, Sass, Bootstrap, ASP.NET, .NET Core, jQuery"""]
        h3 [class' "text-center"] [rawText "Skills"]
        p [] [rawText """Database Management and Design, Debugging in Chrome/Firefox/IE, Database and Code Performance Tuning, Security Best Practices, ReactiveX, Parallel and Asynchronous Programming"""]
        h3 [class' "text-center"] [rawText "Inspiration"]
        p [] [rawText """Coding Horror, Joel Spolsky, The Daily WTF, Mythical Man-Month, C# in Depth, F# for Fun and Profit, Advanced Windowing Functions in T-SQL"""]
        // links to pdf version
        // TODO: add links for various things
        div [class' "row"] [
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
