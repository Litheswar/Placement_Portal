import { useState } from "react";
import { registerStudent } from "../services/authService";
import { Link } from "react-router-dom";

function StudentRegister() {

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    roll_number: "",
    branch: "",
    cgpa: "",
    graduation_year: ""
  });

  const handleChange = (e) => {

    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });

  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    try {

      const data = await registerStudent(
        formData
      );

      alert(data.message);

    } catch (error) {

      alert(
        error.response?.data?.message ||
        "Registration Failed"
      );

    }

  };

  return (
    <div className="container mt-5">

      <div className="row justify-content-center">

        <div className="col-md-8">

          <div className="card shadow">

            <div className="card-body">

              <h2 className="mb-4">
                Student Registration
              </h2>

              <form onSubmit={handleSubmit}>

                <input
                  className="form-control mb-3"
                  name="name"
                  placeholder="Name"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="email"
                  placeholder="Email"
                  onChange={handleChange}
                />

                <input
                  type="password"
                  className="form-control mb-3"
                  name="password"
                  placeholder="Password"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="roll_number"
                  placeholder="Roll Number"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="branch"
                  placeholder="Branch"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="cgpa"
                  placeholder="CGPA"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="graduation_year"
                  placeholder="Graduation Year"
                  onChange={handleChange}
                />

                <button
                  className="btn btn-success"
                  type="submit"
                >
                  Register
                </button>

                <div className="mt-3">
                    <Link to="/login">
                        Back To Login
                    </Link>
                </div>
              </form>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default StudentRegister;