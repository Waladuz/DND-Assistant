from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_content/<content_type>")
def get_content(content_type):
    if content_type == "items":
        # Stylized table instead of list
        return '''
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Item A</td>
                    <td>Category 1</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Item B</td>
                    <td>Category 2</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Item C</td>
                    <td>Category 3</td>
                </tr>
            </table>
        '''
    elif content_type == "text1":
        return "<p>This is some generic text for Button 2.</p>"
    elif content_type == "form":
        return '''
            <form>
                <label for="name">Enter your name:</label>
                <input type="text" id="name" name="name">
                <button type="submit">Submit</button>
            </form>
        '''
    elif content_type == "text2":
        return "<p>This is another wall of text for Button 4.</p>"
    else:
        return "<p>Invalid content request.</p>"

if __name__ == "__main__":
    app.run(debug=True)
