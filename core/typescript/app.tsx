import * as React from "react";
import * as _ from "lodash";
import * as ReactDOM from "react-dom";
import * as ReactDataGrid from "react-data-grid";
class Example extends React.Component {
    _columns: any[];
    _rows: any[];
    constructor(props, context){
        super(props,context);
        this.createRows();
        this._columns = [
            { key: 'id', name: 'ID'},
            { key: 'title', name: 'Title'},
            { key: 'count', name: 'Count'}
        ];
        this.state = null;
        this.rowGetter = this.rowGetter.bind(this);
    }
    createRows () {
        this._rows = _.times(5, x => ({
            id: x, 
            title: 'Title ' + x, 
            count: x *100}));
    }
    rowGetter (i: number) {
        return this._rows[i];
    }
    render() {
        return (
            <ReactDataGrid
                columns={this._columns}
                rowGetter={this.rowGetter}
                rowsCount={this._rows.length}
                minHeight={500}
                />
        );
    }
}
ReactDOM.render(
    <div>
        <h1>Hello, Welcome to the first page</h1>
        <Example/>
    </div>,
    document.getElementById("root")
);