
# main.py

import sys
from PySide6.QtWidgets import QApplication
from window import LiveGraph

def main():
    app = QApplication( sys.argv )
    live_graph = LiveGraph()
    live_graph.show()

    # Input loop
    while True:
        try:
            value_input = input( "Enter numbers to plot (comma-separated or 'exit' to quit ): ")
            if value_input.lower() == 'exit':
                break

            # convert input to a list of floats
            values = list( map( float, value_input.split(',') ))
            live_graph.add_data( values )

        except ValueError:
            print( "Invalid input. Please enter numbers separated by commas." )

        except Exception as e:
            print( f"An error occurred: {e}" )

    sys.exit( app.exec() )

if __name__ == "__main__":
    main()

