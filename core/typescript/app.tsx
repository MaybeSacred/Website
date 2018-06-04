import * as React from "react";
import * as _ from "lodash";
import * as ReactDOM from "react-dom";
import * as ReactDataGrid from "react-data-grid";
import update from "immutability-helper";
import { Holding, Asset, Guid } from "./Holding";
import { HoldingViewModel } from "./HoldingViewModel";
import { FirstComponent } from "./FirstComponent";
import Portfolio from "./Portfolio";
function fromHolding(holding: Holding, portfolio: Portfolio) {
    const p = portfolio.totalValue;
    const pct = 0;//holding.currentShares * holding.asset.price / (portfolio.totalValue || 1);
    return new HoldingViewModel(holding.asset.symbol,
        holding.asset.price, holding.currentShares,
        holding.desiredPercentage, pct, 0);
}
interface Props {}
interface State {
    rows: Holding[]
}
class Example extends React.Component<Props,State> {
    _columns: any[];
    constructor(props, context) {
        super(props, context);
        this._columns = [
            { key: 'symbol', name: 'Symbol', editable: true },
            { key: 'currentPrice', name: 'Current Price', editable: true },
            { key: 'currentShares', name: 'Current Shares', editable: true },
            { key: 'desiredPercentage', name: 'Desired Percentage', editable: true },
            { key: 'currentPercentage', name: 'Current Percentage', editable: true },
            { key: 'desiredShares', name: 'Desired Shares', editable: true },
            { key: 'description', name: 'Description', editable: true }
        ];
        this.state = { rows: this.createRows() };
        this.rowGetter = this.rowGetter.bind(this);
    }
    createRows() {
        return _.times(5, x => new Holding(
            Guid.new(),
            new Asset(`VOO${x}`, 100 + x),
            15,
            1));
    }
    rowGetter(i: number) {
        return this.state.rows[i];
    }
    handleGridRowsUpdated = ({ fromRow, toRow, updated }) => {
        let rows = this.state.rows.slice();
        for (let i = fromRow; i <= toRow; i++) {
            //rows[i] = update(rows[i], { $merge: updated });
        }
        this.setState({ rows });
    };
    render() {
        return (
            <ReactDataGrid
                enableCellSelect={true}
                columns={this._columns}
                rowGetter={this.rowGetter}
                rowsCount={this.state.rows.length}
                minHeight={500}
                onGridRowsUpdated={this.handleGridRowsUpdated}
            />
        );
    }
}

ReactDOM.render(
    <div>
        <h1>Hello, Welcome to the first page</h1>
        <Example />
    </div>,
    document.getElementById("root")
);