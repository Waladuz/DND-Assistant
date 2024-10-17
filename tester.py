import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk


class GridCanvasApp:
    def __init__(self, root, image_path, grid_size=50):
        self.root = root
        self.grid_size = grid_size

        # Create a canvas
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        # Load the image using PIL
        self.image = Image.open(image_path)
        self.photo_image = ImageTk.PhotoImage(self.image)

        # Add the image to the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)

        # Draw the grid on the canvas
        self.draw_grid()

        # Create the right-click context menu
        self.create_context_menu()

        # Bind a right-click event to the canvas
        self.canvas.bind("<Button-3>", self.show_context_menu)

    def draw_grid(self):
        """Draw a grid on top of the image."""
        width = self.canvas.winfo_reqwidth()
        height = self.canvas.winfo_reqheight()

        for i in range(0, width, self.grid_size):
            self.canvas.create_line([(i, 0), (i, height)], tag='grid', fill='black')

        for i in range(0, height, self.grid_size):
            self.canvas.create_line([(0, i), (width, i)], tag='grid', fill='black')

    def create_context_menu(self):
        """Create a right-click context menu."""
        self.menu = Menu(self.canvas, tearoff=0)
        self.menu.add_command(label="Option 1", command=lambda: self.menu_action("Option 1"))
        self.menu.add_command(label="Option 2", command=lambda: self.menu_action("Option 2"))
        self.menu.add_command(label="Option 3", command=lambda: self.menu_action("Option 3"))

    def show_context_menu(self, event):
        """Show the context menu at the clicked position."""
        # Calculate which grid cell was clicked
        grid_x = event.x // self.grid_size * self.grid_size
        grid_y = event.y // self.grid_size * self.grid_size

        print(f"Right-clicked at grid coordinate: ({grid_x}, {grid_y})")

        # Show the context menu at the clicked position
        self.menu.post(event.x_root, event.y_root)

    def menu_action(self, option):
        """Handle context menu actions."""
        print(f"Selected {option} from the menu.")


# Main window
root = tk.Tk()
root.title("Canvas with Right-Click Menu")

# Create an instance of the GridCanvasApp with a background image and grid size
app = GridCanvasApp(root, image_path="maps/map2.png", grid_size=50)

# Run the Tkinter main loop
root.mainloop()
