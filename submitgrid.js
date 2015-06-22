// my first ever javascript! Woo learning!

// Serialise user input sudoku grid and send it off to a flask server somehow.
// TODO: Look up http POST. that sounds promising.

function submitGrid() {
	var grid = [];

	// hehe. puns.
	var atoi = "ABCDEFGHI"

	// loop through rows in html input boxes
	for (row_num=1; row_num<10; row_num++) {
		var row_char = row_num.toString();
		var row = [];

		// loop through columns
		for (i=0; i<9; i++) {
			var col_char = atoi.charAt(i);
			var coord = col_char.concat(row_char)

			var cell_contents = document.getElementById(coord).value;
			if (cell_contents == "") {
				row.push(0);
			} else {
				//TODO: input validation, when I learn how
				row.push(parseInt(cell_contents));
			}
		}
		grid.push(row);
	}
	var gridtext = JSON.stringify(grid);
	//debug
	window.alert(gridtext);
	// holy shit, it worked first try! I'm a genius!
}
