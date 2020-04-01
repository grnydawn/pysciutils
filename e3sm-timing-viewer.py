"""E3SM Timing data viewer"""

import sys
import webbrowser
import tempfile
import shlex

### source : http://bl.ocks.org/dhoboy/1ac430a7ca883e7a8c09

html = """
<!DOCTYPE html>
<meta charset="utf-8">
<style>
body {
  background-color: #d1e5f0;
  font: 14px sans-serif;
}

#container {
  width: 100%;
  height: 100%;
  position: relative;
}

#title {
  font: 26px sans-serif;
  position: absolute;
  top: -40px;
  left: 450px;
}

#FilterableTable {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 40px;
  left: 20px;
}

.SearchBar { 
  display: inline; 
  position: relative;
  left: 1%;
}

.SearchBar input {
  position: relative;
  left: 2%;
}

table { 
  position: absolute;
  top: 40px;
  left: 20px;
  border-collapse: collapse;
  margin-bottom: 20px;
}

table a:link, a:visited { text-decoration: none; }

table a:hover, a:active { text-decoration: underline; }

table, th, td { border: 1px solid black; }

td, th {
  padding: 5px;
  text-align: center;
  height: 20px;
}

th {
  background-color: #4393c3;
  color: #d9f0a3;
}

td { background-color: #92c5de; }

tr:hover td { background-color: #edf8b1; }

</style>
<body>
<script src="https://d3js.org/d3.v3.js"></script>
<script>

var column_names = ["Id", "Name","Processes","Threads","Count", "Walltime-total", \
                    "Walltime-max", "Walltime-min"];
var clicks = {rowid:0, name: 0, processes: 0, threads: 0, count: 0, walltotal: 0,
              wallmax: 0, wallmin: 0};

// draw the table
d3.select("body").append("div")
  .attr("id", "container")

d3.select("#container").append("div")
  .attr("id", "FilterableTable");

d3.select("#FilterableTable").append("h1")
  .attr("id", "title")
  .text("E3SM Timing Viewer")

d3.select("#FilterableTable").append("div")
  .attr("class", "SearchBar")
  .append("p")
    .attr("class", "SearchBar")
    .text("Search By Name:");

d3.select(".SearchBar")
  .append("input")
    .attr("class", "SearchBar")
    .attr("id", "search")
    .attr("type", "text")
    .attr("placeholder", "Search...");
  
var table = d3.select("#FilterableTable").append("table");
table.append("thead").append("tr"); 

var headers = table.select("tr").selectAll("th")
    .data(column_names)
  .enter()
    .append("th")
    .text(function(d) { return d; });

var rows, row_entries, row_entries_no_anchor, row_entries_with_anchor;

var jsondata = '[JSONDATA]';

data = JSON.parse(jsondata);
//d3.json("data.json", function(data) { // loading data from server
  
  // draw table body with rows
  table.append("tbody")

  // data bind
  rows = table.select("tbody").selectAll("tr")
    .data(data, function(d){ return d.id; });
  
  // enter the rows
  rows.enter()
    .append("tr")
  
  // enter td's in each row
  row_entries = rows.selectAll("td")
      .data(function(d) { 
        var arr = [];
        for (var k in d) {
          if (d.hasOwnProperty(k)) {
		    arr.push(d[k]);
          }
        }
        return [arr[0],arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7]];
        //return [arr[6],arr[5],arr[4],arr[3],arr[1],arr[2],arr[0]];
      })
    .enter()
      .append("td") 

  // draw row entries with no anchor 
  row_entries_no_anchor = row_entries.filter(function(d) {
    return (/https?:\/\//.test(d) == false)
  })
  row_entries_no_anchor.text(function(d) { return d; })

  // draw row entries with anchor
  row_entries_with_anchor = row_entries.filter(function(d) {
    return (/https?:\/\//.test(d) == true)  
  })
  row_entries_with_anchor
    .append("a")
    .attr("href", function(d) { return d; })
    .attr("target", "_blank")
  .text(function(d) { return d; })
    
    
  /**  search functionality **/
    d3.select("#search")
      .on("keyup", function() { // filter according to key pressed 
        var searched_data = data,
            text = this.value.trim();
        
        var searchResults = searched_data.map(function(r) {
          var regex = new RegExp("^" + text + ".*", "i");
          if (regex.test(r.name)) { // if there are any results
            return regex.exec(r.name)[0]; // return them to searchResults
          } 
        })
	    
	    // filter blank entries from searchResults
        searchResults = searchResults.filter(function(r){ 
          return r != undefined;
        })
        
        // filter dataset with searchResults
        searched_data = searchResults.map(function(r) {
           return data.filter(function(p) {
            return p.name.indexOf(r) != -1;
          })
        })

        // flatten array 
		searched_data = [].concat.apply([], searched_data)
        
        // data bind with new data
		rows = table.select("tbody").selectAll("tr")
		  .data(searched_data, function(d){ return d.id; })
		
        // enter the rows
        rows.enter()
         .append("tr");
         
        // enter td's in each row
        row_entries = rows.selectAll("td")
            .data(function(d) { 
              var arr = [];
              for (var k in d) {
                if (d.hasOwnProperty(k)) {
		          arr.push(d[k]);
                }
              }
              //return [arr[6],arr[5],arr[4],arr[3],arr[1],arr[2],arr[0]];
              return [arr[0],arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7]];
            })
          .enter()
            .append("td") 

        // draw row entries with no anchor 
        row_entries_no_anchor = row_entries.filter(function(d) {
          return (/https?:\/\//.test(d) == false)
        })
        row_entries_no_anchor.text(function(d) { return d; })

        // draw row entries with anchor
        row_entries_with_anchor = row_entries.filter(function(d) {
          return (/https?:\/\//.test(d) == true)  
        })
        row_entries_with_anchor
          .append("a")
          .attr("href", function(d) { return d; })
          .attr("target", "_blank")
        .text(function(d) { return d; })
        
        // exit
        rows.exit().remove();
      })
    
  /**  sort functionality **/
  headers
    .on("click", function(d) {
      if (d == "Id") {
        clicks.rowid++;
        // even number of clicks
        if (clicks.rowid % 2 == 0) {
          // sort ascending: alphabetically
          rows.sort(function(a,b) { 
            if (a.rowid.toUpperCase() < b.rowid.toUpperCase()) { 
              return -1; 
            } else if (a.rowid.toUpperCase() > b.rowid.toUpperCase()) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.rowid % 2 != 0) { 
          // sort descending: alphabetically
          rows.sort(function(a,b) { 
            if (a.rowid.toUpperCase() < b.rowid.toUpperCase()) { 
              return 1; 
            } else if (a.rowid.toUpperCase() > b.rowid.toUpperCase()) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Name") {
        clicks.name++;
        // even number of clicks
        if (clicks.name % 2 == 0) {
          // sort ascending: alphabetically
          rows.sort(function(a,b) { 
            if (a.name.toUpperCase() < b.name.toUpperCase()) { 
              return -1; 
            } else if (a.name.toUpperCase() > b.name.toUpperCase()) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.name % 2 != 0) { 
          // sort descending: alphabetically
          rows.sort(function(a,b) { 
            if (a.name.toUpperCase() < b.name.toUpperCase()) { 
              return 1; 
            } else if (a.name.toUpperCase() > b.name.toUpperCase()) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Processes") {
	    clicks.processes++;
        // even number of clicks
        if (clicks.processes % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.processes < +b.processes) { 
              return -1; 
            } else if (+a.processes > +b.processes) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.processes % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.processes < +b.processes) { 
              return 1; 
            } else if (+a.processes > +b.processes) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Threads") {
	    clicks.threads++;
        // even number of clicks
        if (clicks.threads % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.threads < +b.threads) { 
              return -1; 
            } else if (+a.threads > +b.threads) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.threads % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.threads < +b.threads) { 
              return 1; 
            } else if (+a.threads > +b.threads) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Count") {
	    clicks.count++;
        // even number of clicks
        if (clicks.count % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.count < +b.count) { 
              return -1; 
            } else if (+a.count > +b.count) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.count % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.count < +b.count) { 
              return 1; 
            } else if (+a.count > +b.count) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Walltime-total") {
	    clicks.walltotal++;
        // even number of clicks
        if (clicks.walltotal % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.walltotal < +b.walltotal) { 
              return -1; 
            } else if (+a.walltotal > +b.walltotal) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.walltotal % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.walltotal < +b.walltotal) { 
              return 1; 
            } else if (+a.walltotal > +b.walltotal) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Walltime-max") {
	    clicks.wallmax++;
        // even number of clicks
        if (clicks.wallmax % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.wallmax < +b.wallmax) { 
              return -1; 
            } else if (+a.wallmax > +b.wallmax) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.wallmax % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.wallmax < +b.wallmax) { 
              return 1; 
            } else if (+a.wallmax > +b.wallmax) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "Walltime-min") {
	    clicks.wallmin++;
        // even number of clicks
        if (clicks.wallmin % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.wallmin < +b.wallmin) { 
              return -1; 
            } else if (+a.wallmin > +b.wallmin) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.wallmin % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.wallmin < +b.wallmin) { 
              return 1; 
            } else if (+a.wallmin > +b.wallmin) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
    }); // end of click listeners
d3.select(self.frameElement).style("height", "780px").style("width", "1150px");	
</script>
"""

def main():

    ret = -1

    # read timing data
    hdr = ("name", "processes", "threads", "count", "walltotal", "wallmax",
              "wallmin")
    rawdata = []

    timingfile = "res/ocnt.txt"

    with open(timingfile) as ft:
        for line in ft:
            line = line.strip()
            if line and line[0] == '"' and line[-1] == ")":
                s = shlex.split(line)
                items = (s[0], s[2], s[3], s[4], s[5], s[6], s[10])
                rawdata.append(items)

    data = ""

    for i0, r in enumerate(rawdata):
        ldata = ['"id":%d' % i0]
        for i1, h in enumerate(hdr):
            v = '"%s"' % r[i1] if h=="name" else r[i1]
            ldata.append('"%s":%s'% (h, v))

        data += "{" + ",".join(ldata) + "},"
    data = data[:-1]
        #data.append("{" + ",".join(ldata) + "}")

    import pdb; pdb.set_trace()
    with tempfile.NamedTemporaryFile('w',
            delete=False, suffix='.html') as fh:
        #fh.write(html.replace("JSONDATA", ",".join(data)))
        fh.write(html.replace("JSONDATA", data))

    # invoke it
    webbrowser.open("file://" + fh.name)

    # return
    return ret

if __name__ == "__main__":
    sys.exit(main())


