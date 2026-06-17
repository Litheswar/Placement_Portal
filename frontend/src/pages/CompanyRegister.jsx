import { useState } from "react";
import { registerCompany } from "../services/authService";
import { Link } from "react-router-dom";

function CompanyRegister() {

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    hr_contact: "",
    website: "",
    industry: "",
    description: ""
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

      const data = await registerCompany(
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
                Company Registration
              </h2>

              <form onSubmit={handleSubmit}>

                <input
                  className="form-control mb-3"
                  name="name"
                  placeholder="Company Name"
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
                  name="hr_contact"
                  placeholder="HR Contact"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="website"
                  placeholder="Website"
                  onChange={handleChange}
                />

                <input
                  className="form-control mb-3"
                  name="industry"
                  placeholder="Industry"
                  onChange={handleChange}
                />

                <textarea
                  className="form-control mb-3"
                  name="description"
                  placeholder="Description"
                  rows="4"
                  onChange={handleChange}
                />

                <button
                  className="btn btn-success"
                  type="submit"
                >
                  Register Company
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

export default CompanyRegister;