import * as React from "react";
import * as _ from "lodash";
import * as ReactDOM from "react-dom";
import * as ReactDataGrid from "react-data-grid";
import update from "immutability-helper";
import {Holding, Asset, Guid}  from "./Holding";
class Example extends React.Component {
    _columns: any[];
    state: {_rows: Holding[]};
    constructor(props, context){
        super(props,context);
        this._columns = [
            { key: 'id', name: 'ID', editable: false },
            { key: 'symbol', name: 'Symbol', editable: true },
            { key: 'currentShares', name: 'Current Shares', editable: true },
            { key: 'desiredPercentage', name: 'Desired Percentage', editable: true },
            { key: 'description', name: 'Description', editable: true }
        ];
        this.state = {_rows: this.createRows()};
        this.rowGetter = this.rowGetter.bind(this);
    }
    createRows () {
        return _.times(5, x => new Holding (
            Guid.new(), 
            new Asset("VOO", 100), 
            15, 
            1));
    }
    rowGetter (i: number) {
        return this.state._rows[i];
    }
    handleGridRowsUpdated = ({fromRow, toRow, updated}) => {
        let rows = this.state._rows.slice();
        for(let i = fromRow; i <= toRow; i++){
            rows[i] = update(rows[i], {$merge: updated});
        }
        this.setState({ _rows: rows });
    };
    render() {
        return (
            <ReactDataGrid
                enableCellSelect={true}
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