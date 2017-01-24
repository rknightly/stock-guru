var googleStocks = require('google-stocks');

googleStocks(['APPL'], function(error, data) {
    console.log(data);
});
