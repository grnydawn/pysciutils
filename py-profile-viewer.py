"""Python Profile Viewer"""

import sys
import webbrowser
import tempfile
import shlex
import argparse

### D3 source : http://bl.ocks.org/dhoboy/1ac430a7ca883e7a8c09

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

var column_names = ["Row-id", "NCalls", "TotTime","TotTime per Call","CumTime", \
                    "CumTime per Call", "Filename:Lineno(Function)"];
var clicks = {rowid: 0, ncalls:0, tottime: 0, ttpercall: 0, cumtime: 0, \
              ctpercall: 0, filename: 0};

// draw the table
d3.select("body").append("div")
  .attr("id", "container")

d3.select("#container").append("div")
  .attr("id", "FilterableTable");

d3.select("#FilterableTable").append("h1")
  .attr("id", "title")
  .text("Python Profiler Timing Viewer")

d3.select("#FilterableTable").append("div")
  .attr("class", "SearchBar")
  .append("p")
    .attr("class", "SearchBar")
    .text("Search By Filename:");

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

var rows, row_entries;

var jsondata = '[JSONDATA]';

data = JSON.parse(jsondata);
  
  // draw table body with rows
  table.append("tbody")

  // data bind
  rows = table.select("tbody").selectAll("tr")
    .data(data, function(d){ return d.rowid; });
  
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
        return [arr[0],arr[1],arr[2],arr[3],arr[4],arr[5], arr[6]];
      })
    .enter()
      .append("td") 

  row_entries.text(function(d) { return d; })

  /**  search functionality **/
    d3.select("#search")
      .on("keyup", function() { // filter according to key pressed 
        var searched_data = data,
            text = this.value.trim();
        
        var searchResults = searched_data.map(function(r) {
          var regex = new RegExp("^" + text + ".*", "i");
          if (regex.test(r.filename)) { // if there are any results
            return regex.exec(r.filename)[0]; // return them to searchResults
          } 
        })
	    
	// filter blank entries from searchResults
        searchResults = searchResults.filter(function(r){ 
          return r != undefined;
        })
        
        // filter dataset with searchResults
        searched_data = searchResults.map(function(r) {
           return data.filter(function(p) {
            return p.filename.indexOf(r) != -1;
          })
        })

        // flatten array 
	searched_data = [].concat.apply([], searched_data)
        
        // data bind with new data
	rows = table.select("tbody").selectAll("tr")
		  .data(searched_data, function(d){ return d.rowid; })
		
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
              return [arr[0],arr[1],arr[2],arr[3],arr[4],arr[5],arr[6]];
            })
          .enter()
            .append("td") 

        row_entries.text(function(d) { return d; })
        // exit
        rows.exit().remove();
      })


  /**  sort functionality **/
  headers
    .on("click", function(d) {
      if (d == "Row-id") {
	clicks.rowid++;
        // even number of clicks
        if (clicks.rowid % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.rowid < +b.rowid) { 
              return -1; 
            } else if (+a.rowid > +b.rowid) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.rowid % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.rowid < +b.rowid) { 
              return 1; 
            } else if (+a.rowid > +b.rowid) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 

      if (d == "Filename:Lineno(Function)") {
        clicks.filename++;
        // even number of clicks
        if (clicks.filename % 2 == 0) {
          // sort ascending: alphabetically
          rows.sort(function(a,b) { 
            if (a.filename.toUpperCase() < b.filename.toUpperCase()) { 
              return -1; 
            } else if (a.filename.toUpperCase() > b.filename.toUpperCase()) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.filename % 2 != 0) { 
          // sort descending: alphabetically
          rows.sort(function(a,b) { 
            if (a.filename.toUpperCase() < b.filename.toUpperCase()) { 
              return 1; 
            } else if (a.filename.toUpperCase() > b.filename.toUpperCase()) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 

      if (d == "NCalls") {
	    clicks.ncalls++;
        // even number of clicks
        if (clicks.ncalls % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.ncalls < +b.ncalls) { 
              return -1; 
            } else if (+a.ncalls > +b.ncalls) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.ncalls % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.ncalls < +b.ncalls) { 
              return 1; 
            } else if (+a.ncalls > +b.ncalls) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "TotTime") {
	    clicks.tottime++;
        // even number of clicks
        if (clicks.tottime % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.tottime < +b.tottime) { 
              return -1; 
            } else if (+a.tottime > +b.tottime) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.tottime % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.tottime < +b.tottime) { 
              return 1; 
            } else if (+a.tottime > +b.tottime) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "TotTime per Call") {
	    clicks.ttpercall++;
        // even number of clicks
        if (clicks.ttpercall % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.ttpercall < +b.ttpercall) { 
              return -1; 
            } else if (+a.ttpercall > +b.ttpercall) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.ttpercall % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.ttpercall < +b.ttpercall) { 
              return 1; 
            } else if (+a.ttpercall > +b.ttpercall) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "CumTime") {
	    clicks.cumtime++;
        // even number of clicks
        if (clicks.cumtime % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.cumtime < +b.cumtime) { 
              return -1; 
            } else if (+a.cumtime > +b.cumtime) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.cumtime % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.cumtime < +b.cumtime) { 
              return 1; 
            } else if (+a.cumtime > +b.cumtime) { 
              return -1; 
            } else {
              return 0;
            }
          });
        }
      } 
      if (d == "CumTime per Call") {
	    clicks.ctpercall++;
        // even number of clicks
        if (clicks.ctpercall % 2 == 0) {
          // sort ascending: numerically
          rows.sort(function(a,b) { 
            if (+a.ctpercall < +b.ctpercall) { 
              return -1; 
            } else if (+a.ctpercall > +b.ctpercall) { 
              return 1; 
            } else {
              return 0;
            }
          });
        // odd number of clicks  
        } else if (clicks.ctpercall % 2 != 0) { 
          // sort descending: numerically
          rows.sort(function(a,b) { 
            if (+a.ctpercall < +b.ctpercall) { 
              return 1; 
            } else if (+a.ctpercall > +b.ctpercall) { 
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

    parser = argparse.ArgumentParser(description='Python Profiler Timing Data Viewer.')
    parser.add_argument('timingfile', help='path to timing data file')
    parser.add_argument('-o', '--output', help='path to html output file')

    args = parser.parse_args()

#var clicks = {rowid: 0, ncalls:0, tottime: 0, ttpercall: 0, cumtime: 0, \
              #ctpercall: 0, filename: 0};

    # read timing data
    hdr = ("ncalls", "tottime", "ttpercall", "cumtime", "ctpercall",
            "filename")
    rawdata = []

    with open(args.timingfile) as ft:
        for line in ft:
            elems = line.strip().split(None, 5)
            if len(elems)>0 and elems[0].isdigit() and elems[-1][-1] in (")", "}"):
                rawdata.append(elems)

    data = ""

    for i0, r in enumerate(rawdata):
        ldata = ['"rowid":%d' % i0]
        for i1, h in enumerate(hdr):
            if h=="filename":
                v = '"%s"' % r[i1].replace('"', r'\"').replace("'", r"\'")
            else:
                v = r[i1]
            ldata.append('"%s":%s'% (h, v))

        data += "{" + ",".join(ldata) + "},"
    data = data[:-1]

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(html.replace("JSONDATA", data))
    else:
        with tempfile.NamedTemporaryFile('w',
                delete=False, suffix='.html') as fh:
            fh.write(html.replace("JSONDATA", data))

        # invoke it
        webbrowser.open("file://" + fh.name)

    # return
    return 0

if __name__ == "__main__":
    sys.exit(main())
