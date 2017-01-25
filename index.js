var googleFinance = require('google-finance');

var SYMBOL = "NASDAQ:AAPL";
var START_DATE = "2017-01-01";
var END_DATE = "2017-01-24";

googleFinance.historical({
    symbol: SYMBOL,
    from: START_DATE,
    to: END_DATE
}, function (err, quotes) {
    if (err) {
        console.log("An error occured");
    } else {
        console.log(quotes);
    }
});
