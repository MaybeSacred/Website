module Types
open Suave.FunctionalViewEngine
open System
type Content = | Text of string | Nodes of (unit -> XmlNode list)
// TODO: may need to add a Script list for additional scripts that need to be injected in the proper place
/// A website page
type Page = { 
    /// Title of the page
    Title: string; 
    /// Created timestamp
    Created: DateTime;
    /// Last modified timestamp
    Modified: DateTime; 
    /// Content to be rendered
    Content: Content }
let textify = renderHtmlNodes >> Text