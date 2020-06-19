Map of Sweden #4
****************

:date: 2020-02-01
:modified: 2020-02-01
:tags: D3, Maps
:summary: A note on making maps #4

By previous posts, I have shown how to create a map of Sweden, get meteorological observations from SMHI and visualize
this on a map. What is lacking, is some decorations and interactions with the map.

In this post I'll explain how to add a legend, show tool tip when hoovering the mouse above the map and some other
miscellaneous tasks.

Adding a legend
+++++++++++++++
This is straightforward using a D3 library: **d3-legend.js**. Use this by downloading in the html file such as:

.. code-block:: html

    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3-legend/1.1.0/d3-legend.js"></script>

Then I use the library like this

.. code-block:: javascript

    let legendLinear = d3.legend.color()
        .shapeWidth(15)
        .cells(colors.length)
        .orient('vertical')
        .scale(colors);

    svg.call(legendLinear);

Above, I'm using an array variable colors (see `part 3 <{filename}./Map_of_Sweden_part_2.rst>`__ or below) to determine
how many legend cells that should be used. The orientation is vertical.

Map with legend
+++++++++++++++
The next thing I want to add is **tooltip** that pops up when I move the mouse over the map. It should show the name of
the station and the value of the observation. To do this I will be using `bootstrap <https://getbootstrap.com/>`_.
Bootstrap is used to build responsive web-pages, meaning that the web-page renders well on a variety of devices,
ie screen sizes. Included is support for tooltips. The javascript code looks like so

.. code-block:: javascript

    function showTooltip(d) {
        let element = d3.selectAll(".dot" + d.point.nr);

        $(element).popover({
            placement: 'auto top',
            container: '#chart',
            trigger: 'manual',
            html: true,
            content: function () {
                return "<span style='font-size: 12px; text-align: center;'>" +
                    d.point.station + ": " +
                    d.point.val + "</span>";
            }
        });
        $(element).popover('show');
    }

    function removeTooltip() {
        $('.popover').each(function () {
            $(this).remove();
        });
    }

    svg.selectAll("voronoi")
        .data(voronoi(values.val))
        .enter()
            .append("path")
            .attr("clip-path", "url(#swe-clip)")
            .attr("fill", function (d) {
                return colors(d.point.val)
            })
            .attr("d", function (d) {
                return "M" + d.join("L") + "Z";
            })
            .attr("style", function (d) {
                return "stroke: " + colors(d.point.val)
            })
            .on('mouseover', showTooltip)
            .on('mouseout', removeTooltip);

    svg.selectAll("dots")
        .data(values.val)
        .enter()
            .append("circle")
            .attr("class", function (d) {
                return "dot" + d.nr;
            })
            .style("fill", function (d) {
                return "none";
            })
            .attr("cx", function (d) {
                return d.x
            })
            .attr("cy", function (d) {
                return d.y
            })
            .attr("r", function (d) {
                return 1
            });

In the **<head>** section, include this to have access to bootstrap.

.. code-block:: html

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/js/bootstrap.min.js"></script>

Some comments on the javascript for tooltip

* The voronoi diagram (or mapping of Sweden) is extended with two events **mouseover** and **mouseout** where
  **showTooltip** and **RemoveTooltip** are called respectively.
* **showTooltip** first selects the element with the unique id **"dotN"** (N = 1, 2, 3, ...)
  then calls the **popover** function with relevant parameter values.  The **content** parameter generates HTML code
  with the actual values for the station name and observation, through the "d" parameter.
* **removeTooltip** removes the tooltip (obviously...) when the mouse is moved outside focus.
* The trick here is the unique **"dotN"**. This is generated in the last part of the javascript code. To the "class"
  attribute I generate the string "dot" and the add a number. Remember the javascript code for "get_values" as shown in
  `part 3 <{filename}./Map_of_Sweden_part_3.rst>`__ of these blog postings? It is shown below. In that code I generate a "nr" field in the resulting element.
  Now I am using this to create the unique **"dotN"**.

  Ok, why?

  Well, we need it in the **showToolTip** and it will position the tooltip popup at the right place in the map.
  In the code, I actually draw a small circle at the [x, y] coordinates, which is the projected longitude/latitude
  values of the station making the observation. However, I draw the circle with the same background color as the
  voronoi cell so they are invisible. To show them as a back dot on the map, simply change return value of the fill
  style-attribute to "black". (The actual reason for drawing a circle for the metereological station invisble, is that
  I later on want to dynamically - at user interaction - turn them on/off).
  Here is the **get_values** code as stated in `part 3 <{filename}./Map_of_Sweden_part_3.rst>`__.

.. code-block:: javascript

    function get_values(key) {
        let lst = [];
        let max_val = min_val = weather[key][0].val;

        for (let stn = 0; stn < weather[key].length; stn++) {
            if (weather[key][stn].active) {
                // Transform coordinates according to the selected projection\
                let xy = projection([weather[key][stn].lon, weather[key][stn].lat]);
                lst.push({
                    x: xy[0],
                    y: xy[1],
                    station: weather[key][stn].station,
                    val: weather[key][stn].val,
                    nr: stn.toString()
                });
                max_val = Math.max(max_val, weather[key][stn].val);
                min_val = Math.min(min_val, weather[key][stn].val);
            }
        }
        return {key: key, val: lst, max: max_val, min: min_val, date: weather.date};
    }

The complete listing is `here <https://github.com/Wolfrax/clover/blob/master/index.html>`__