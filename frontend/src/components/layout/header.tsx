'use client';

import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { LogOut, Settings, User, Calendar, Menu } from 'lucide-react';

interface HeaderProps {
  variant?: 'public' | 'dashboard';
}

export function Header({ variant = 'public' }: HeaderProps) {
  const { data: session, status } = useSession();
  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant';

  const handleLogout = () => {
    signOut({ callbackUrl: '/' });
  };

  if (variant === 'dashboard') {
    return (
      <header className="border-b bg-white">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded bg-orange-500 flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {restaurantName.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="font-semibold text-gray-900">{restaurantName} Dashboard</span>
            </Link>
          </div>

          <nav className="hidden md:flex items-center space-x-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 px-3 py-2">
              Overview
            </Link>
            <Link href="/dashboard/menu" className="text-gray-600 hover:text-gray-900 px-3 py-2">
              Menu
            </Link>
            <Link href="/dashboard/reservations" className="text-gray-600 hover:text-gray-900 px-3 py-2">
              Reservations
            </Link>
            <Link href="/dashboard/settings" className="text-gray-600 hover:text-gray-900 px-3 py-2">
              Settings
            </Link>
          </nav>

          <div className="flex items-center space-x-4">
            {session?.user && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        {session.user.name?.charAt(0).toUpperCase() || 'U'}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem className="flex items-center">
                    <User className="mr-2 h-4 w-4" />
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">{session.user.name}</p>
                      <p className="text-xs text-gray-500">{session.user.email}</p>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      Settings
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="h-10 w-10 rounded-full bg-orange-500 flex items-center justify-center">
              <span className="text-white font-bold text-lg">
                {restaurantName.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="font-bold text-xl text-gray-900">{restaurantName}</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              href="/" 
              className="text-gray-600 hover:text-gray-900 active:text-orange-600 font-medium transition-colors duration-150 px-2 py-1 rounded-md hover:bg-gray-50 active:bg-orange-50"
            >
              Home
            </Link>
            <Link 
              href="/menu" 
              className="text-gray-600 hover:text-gray-900 active:text-orange-600 font-medium transition-colors duration-150 px-2 py-1 rounded-md hover:bg-gray-50 active:bg-orange-50"
            >
              Menu
            </Link>
            <Link 
              href="/book" 
              className="text-gray-600 hover:text-gray-900 active:text-orange-600 font-medium transition-colors duration-150 px-2 py-1 rounded-md hover:bg-gray-50 active:bg-orange-50"
            >
              Reservations
            </Link>
            <Link 
              href="/contact" 
              className="text-gray-600 hover:text-gray-900 active:text-orange-600 font-medium transition-colors duration-150 px-2 py-1 rounded-md hover:bg-gray-50 active:bg-orange-50"
            >
              Contact
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <Link href="/book">
              <Button className="bg-orange-500 hover:bg-orange-600 text-white">
                <Calendar className="mr-2 h-4 w-4" />
                Book Table
              </Button>
            </Link>
            
            {status === 'authenticated' ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <User className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard">Dashboard</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout}>
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link href="/auth/login">
                <Button variant="ghost" size="sm">
                  Staff Login
                </Button>
              </Link>
            )}

            {/* Mobile menu button */}
            <Button variant="ghost" size="sm" className="md:hidden">
              <Menu className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}