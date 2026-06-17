import { useState } from "react";
import { loginUser } from "../services/authService";
import { Link, useNavigate } from "react-router-dom";

function Login(){
    const navigate = useNavigate();

    const [role, setRole] = useState("student");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = async (e) => {
  e.preventDefault();

  try {

    const data = await loginUser(
      role,
      email,
      password
    );

    console.log(data);

    localStorage.setItem(
  "token",
  data.access_token
);

localStorage.setItem(
  "role",
  data.role
);

if (data.role === "admin") {
  navigate("/admin/dashboard");
}

if (data.role === "student") {
  navigate("/student/dashboard");
}

if (data.role === "company") {
  navigate("/company/dashboard");
}

  } catch (error) {

    alert(
      error.response?.data?.message ||
      "Login Failed"
    );

  }
};

    return (
        <div className="container">
            <div className="row justify-content-center mt-5">
                <div className="col-md-6">

                    <div className="card shadow">
                        <div className="card-body p-4">

                            <h2 className="text-center mb-4">
                                Placement Portal Login
                            </h2>

                            <form onSubmit={handleSubmit}>

                                <div className="mb-3">
                                    <label className="form-label">
                                        Role
                                    </label>

                                    <select className="form-select"
                                    value={role} onChange={(e) => setRole(e.target.value)}
                                    >
                                        <option value="admin">Admin</option>
                                        <option value="student">Student</option>
                                        <option value="company">Company</option>
                                    </select>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">
                                        Email
                                    </label>

                                    <input type="email" className="form-control"
                                        placeholder="Enter Email" value={email}
                                        onChange={(e) => 
                                            setEmail(e.target.value)
                                        }
                                        required
                                    />
                                </div>

                                <div className="mb-4">
                                    <label className="form-label">
                                        Password
                                    </label>

                                    <input type="password" className="form-control"
                                        placeholder="Enter Password" value={password}
                                        onChange={
                                            (e) => setPassword(e.target.value)
                                        }
                                        required
                                    />
                                </div>

                                <button type="submit" className="btn btn-primary w-100">
                                    Login
                                </button>

                                <div className="text-center mt-3">

                                     <p>
                                 Student?
    <Link
      to="/register/student"
      className="ms-2"
    >
      Register Here
    </Link></p>

  <p>
    Company?
    <Link
      to="/register/company"
      className="ms-2"
    >
      Register Here
    </Link>
  </p>

</div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login;