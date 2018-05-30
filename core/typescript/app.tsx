import * as React from "react";
import * as _ from "lodash";
import * as ReactDOM from "react-dom";
import * as ReactDataGrid from "react-data-grid";
import * as immutability from "immutability-helper";
class Example extends React.Component {
    _columns: any[];
    state: {_rows: any[]};
    constructor(props, context){
        super(props,context);
        this.createRows();
        this._columns = [
            { key: 'id', name: 'ID', editable: true },
            { key: 'title', name: 'Title', editable: true },
            { key: 'count', name: 'Count', editable: true }
        ];
        this.state = {_rows: this.createRows()};
        this.rowGetter = this.rowGetter.bind(this);
    }
    createRows () {
        return _.times(5, x => ({
            id: x, 
            title: 'Title ' + x, 
            count: x *100}));
    }
    rowGetter (i: number) {
        return this.state._rows[i];
    }
    handleGridRowsUpdated = ({fromRow, toRow, updated}) => {
        let rows = this.state._rows.slice();
        
        this.setState({ rows });
    };
    render() {
        return (
            <ReactDataGrid
                columns={this._columns}
                rowGetter={this.rowGetter}
                rowsCount={this.state._rows.length}
                minHeight={500}
                onGridRowsUpdated={this.handleGridRowsUpdated}
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