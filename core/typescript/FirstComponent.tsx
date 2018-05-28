import * as React from "react";
let Logo = "https://logrocket.com/img/logo.png";
export default class FirstComponent extends React.Component <{}> {
    render() {
        return (
            <div>
                <h1>A simple component</h1>
                <div>
                    <img src={Logo}/>
                </div>
                <p>I am a component</p>
            </div>
        );
    }
}