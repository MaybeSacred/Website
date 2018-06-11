import ReactTable from "react-table";
import * as React from "react";
import * as _ from "lodash";
import * as ReactDOM from "react-dom";
import { Holding, Asset, Guid } from "./Holding";
import { FirstComponent } from "./FirstComponent";
import treeTableHOC from "react-table/lib/hoc/treeTable";
import "react-table/react-table.css";

const TreeTable = treeTableHOC(ReactTable);

interface Props {}
interface State {
    data: Holding[]
}

export class Example extends React.Component<Props,State> {
    constructor(props, context) {
        super(props, context);
        this.state = { data: this.createRows() };
    }
    createRows() {
        return _.times(5, x => new Holding(
            Guid.new(),
            "Roth",
            new Asset(`VOO${x}`, 100 + x),
            15,
            1));
    }
    render() {
        return (
        <TreeTable
            data={this.state.data}
            pivotBy={["portfolio"]}
            columns={[
                {
                    Header: "Portfolio",
                    accessor: "portfolio"
                },
                {
                    id: 'symbol',
                    Header: "Symbol",
                    accessor: x => x.asset.symbol
                },
                {
                    id: 'price',
                    Header: "Price",
                    accessor: x => x.asset.price
                },
                {
                    Header: "Current Shares",
                    accessor: "currentShares"
                },
                {
                    Header: "Desired Percentage",
                    accessor: "desiredPercentage"
                },
                {
                    Header: "Description",
                    accessor: "description"
                }
            ]}
            defaultPageSize={10}
        />);
    }
}

