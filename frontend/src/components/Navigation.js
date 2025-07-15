import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Users, 
  Camera, 
  History,
  Activity
} from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/admin', label: 'Admin Panel', icon: Users },
    { path: '/recognize', label: 'Face Recognition', icon: Camera },
    { path: '/history', label: 'History', icon: History },
  ];

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/dashboard" className="nav-brand">
          <Activity size={24} />
          Face Recognition System
        </Link>
        
        <ul className="nav-links">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <Link 
                  to={item.path} 
                  className={`nav-link ${isActive ? 'active' : ''}`}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
