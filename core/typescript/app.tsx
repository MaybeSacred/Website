import * as React from "react";
import * as ReactDOM from "react-dom";
import FirstComponent from './FirstComponent';
import UserComponent from './UserComponent';
ReactDOM.render(
    <div>
        <h1>Hello, Welcome to the first page</h1>
        <FirstComponent/>
        <UserComponent name="Loggg" age={105} address="hahaha" dob={new Date()} />
    </div>,
    document.getElementById("root")
);