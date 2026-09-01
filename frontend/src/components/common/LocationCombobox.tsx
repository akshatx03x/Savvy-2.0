'use client';

import React, { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';

interface LocationComboboxProps {
  countryValue: string;
  regionValue: string;
  cityValue?: string;
  onCountryChange: (countryName: string, countryCode: string) => void;
  onRegionChange: (regionName: string, regionCode?: string) => void;
  onCityChange?: (cityName: string) => void;
}

export default function LocationCombobox({
  countryValue,
  regionValue,
  cityValue = '',
  onCountryChange,
  onRegionChange,
  onCityChange,
}: LocationComboboxProps) {
  const [countries, setCountries] = useState<Array<{ code: string; name: string; iso_code: string }>>([]);
  const [regions, setRegions] = useState<Array<{ id: string; name: string; code: string }>>([]);
  const [cities, setCities] = useState<Array<{ id: string; name: string }>>([]);

  const [countryQuery, setCountryQuery] = useState(countryValue || '');
  const [regionQuery, setRegionQuery] = useState(regionValue || '');
  const [cityQuery, setCityQuery] = useState(cityValue || '');

  const [selectedCountryCode, setSelectedCountryCode] = useState<string>('');
  const [selectedRegionCode, setSelectedRegionCode] = useState<string>('');

  const [showCountryDropdown, setShowCountryDropdown] = useState(false);
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);
  const [showCityDropdown, setShowCityDropdown] = useState(false);

  const countryRef = useRef<HTMLDivElement>(null);
  const regionRef = useRef<HTMLDivElement>(null);
  const cityRef = useRef<HTMLDivElement>(null);

  // Sync external props to state
  useEffect(() => {
    setCountryQuery(countryValue || '');
  }, [countryValue]);

  useEffect(() => {
    setRegionQuery(regionValue || '');
  }, [regionValue]);

  useEffect(() => {
    setCityQuery(cityValue || '');
  }, [cityValue]);

  // Fetch countries
  useEffect(() => {
    const loadCountries = async () => {
      try {
        const res = await api.getLocationsCountries(countryQuery);
        setCountries(res);
      } catch (e) {
        setCountries([
          { code: 'US', name: 'United States', iso_code: 'USA' },
          { code: 'CA', name: 'Canada', iso_code: 'CAN' },
          { code: 'GB', name: 'United Kingdom', iso_code: 'GBR' },
          { code: 'IN', name: 'India', iso_code: 'IND' },
          { code: 'AU', name: 'Australia', iso_code: 'AUS' },
          { code: 'DE', name: 'Germany', iso_code: 'DEU' },
        ]);
      }
    };
    loadCountries();
  }, [countryQuery]);

  // Fetch regions whenever country code changes
  useEffect(() => {
    if (!selectedCountryCode) {
      setRegions([]);
      return;
    }
    const loadRegions = async () => {
      try {
        const res = await api.getLocationsRegions(selectedCountryCode, regionQuery);
        setRegions(res);
      } catch (e) {
        setRegions([]);
      }
    };
    loadRegions();
  }, [selectedCountryCode, regionQuery]);

  // Fetch cities whenever region changes
  useEffect(() => {
    if (!selectedCountryCode || !selectedRegionCode) {
      setCities([]);
      return;
    }
    const loadCities = async () => {
      try {
        const res = await api.getLocationsCities(selectedCountryCode, selectedRegionCode, cityQuery);
        setCities(res);
      } catch (e) {
        setCities([]);
      }
    };
    loadCities();
  }, [selectedCountryCode, selectedRegionCode, cityQuery]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (countryRef.current && !countryRef.current.contains(e.target as Node)) {
        setShowCountryDropdown(false);
      }
      if (regionRef.current && !regionRef.current.contains(e.target as Node)) {
        setShowRegionDropdown(false);
      }
      if (cityRef.current && !cityRef.current.contains(e.target as Node)) {
        setShowCityDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectCountry = (country: { code: string; name: string }) => {
    setCountryQuery(country.name);
    setSelectedCountryCode(country.code);
    onCountryChange(country.name, country.code);

    // Cascading clear: Clear region and city when country changes!
    setRegionQuery('');
    setSelectedRegionCode('');
    onRegionChange('', '');

    setCityQuery('');
    if (onCityChange) onCityChange('');

    setShowCountryDropdown(false);
  };

  const handleSelectRegion = (region: { code: string; name: string }) => {
    setRegionQuery(region.name);
    setSelectedRegionCode(region.code);
    onRegionChange(region.name, region.code);

    // Cascading clear: Clear city when region changes!
    setCityQuery('');
    if (onCityChange) onCityChange('');

    setShowRegionDropdown(false);
  };

  const handleSelectCity = (cityName: string) => {
    setCityQuery(cityName);
    if (onCityChange) onCityChange(cityName);
    setShowCityDropdown(false);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Country Input */}
      <div className="relative" ref={countryRef}>
        <label className="block text-xs font-medium text-slate-700 mb-1">Country</label>
        <input
          type="text"
          value={countryQuery}
          onChange={(e) => {
            setCountryQuery(e.target.value);
            setShowCountryDropdown(true);
            if (!e.target.value) {
              onCountryChange('', '');
              setRegionQuery('');
              setSelectedRegionCode('');
              onRegionChange('', '');
              setCityQuery('');
              if (onCityChange) onCityChange('');
              setSelectedCountryCode('');
            }
          }}
          onFocus={() => setShowCountryDropdown(true)}
          placeholder="Type country..."
          className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 transition"
        />

        {showCountryDropdown && countries.length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-30 max-h-48 overflow-y-auto">
            {countries.map((c) => (
              <button
                key={c.code}
                type="button"
                onClick={() => handleSelectCountry(c)}
                className="w-full text-left px-3 py-2 text-xs text-slate-800 hover:bg-slate-100 flex items-center justify-between transition"
              >
                <span>{c.name}</span>
                <span className="text-[10px] text-slate-400 font-mono">{c.code}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Region Input */}
      <div className="relative" ref={regionRef}>
        <label className="block text-xs font-medium text-slate-700 mb-1">Region / State</label>
        <input
          type="text"
          value={regionQuery}
          disabled={!selectedCountryCode && !countryValue}
          onChange={(e) => {
            setRegionQuery(e.target.value);
            setShowRegionDropdown(true);
            if (!e.target.value) {
              onRegionChange('', '');
              setCityQuery('');
              if (onCityChange) onCityChange('');
            }
          }}
          onFocus={() => setShowRegionDropdown(true)}
          placeholder={selectedCountryCode || countryValue ? 'Select or type region...' : 'Select country first'}
          className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 disabled:bg-slate-100 disabled:text-slate-400 transition"
        />

        {showRegionDropdown && regions.length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-30 max-h-48 overflow-y-auto">
            {regions.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => handleSelectRegion(r)}
                className="w-full text-left px-3 py-2 text-xs text-slate-800 hover:bg-slate-100 flex items-center justify-between transition"
              >
                <span>{r.name}</span>
                <span className="text-[10px] text-slate-400 font-mono">{r.code}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* City Input (Optional) */}
      <div className="relative" ref={cityRef}>
        <label className="block text-xs font-medium text-slate-700 mb-1">City (Optional)</label>
        <input
          type="text"
          value={cityQuery}
          disabled={!selectedRegionCode && !regionValue}
          onChange={(e) => {
            setCityQuery(e.target.value);
            setShowCityDropdown(true);
            if (onCityChange) onCityChange(e.target.value);
          }}
          onFocus={() => setShowCityDropdown(true)}
          placeholder={selectedRegionCode || regionValue ? 'Select or type city...' : 'Select region first'}
          className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 disabled:bg-slate-100 disabled:text-slate-400 transition"
        />

        {showCityDropdown && cities.length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-30 max-h-48 overflow-y-auto">
            {cities.map((ct) => (
              <button
                key={ct.id}
                type="button"
                onClick={() => handleSelectCity(ct.name)}
                className="w-full text-left px-3 py-2 text-xs text-slate-800 hover:bg-slate-100 transition"
              >
                <span>{ct.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
