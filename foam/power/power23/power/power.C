/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2013 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "power.H"
#include "volFields.H"
#include "dictionary.H"
#include "Time.H"
#include "wordReList.H"

#include "incompressible/singlePhaseTransportModel/singlePhaseTransportModel.H"
#include "incompressible/RAS/RASModel/RASModel.H"
#include "incompressible/LES/LESModel/LESModel.H"

#include "fluidThermo.H"
#include "compressible/RAS/RASModel/RASModel.H"
#include "compressible/LES/LESModel/LESModel.H"

//#include "porosityModel.H"

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

namespace Foam
{
defineTypeNameAndDebug(power, 0);
}


// * * * * * * * * * * * * Protected Member Functions  * * * * * * * * * * * //

void Foam::power::writeFileHeader(const label i)
{
    file()
        << "# Time" << tab
        << "power(total, pressure, viscous) ";
    file()<< endl;
}

// Berechnung des Extraspannungstensors
Foam::tmp<Foam::volSymmTensorField> Foam::power::devRhoReff() const
{
    if (obr_.foundObject<compressible::RASModel>("RASProperties"))
    {
        const compressible::RASModel& ras
            = obr_.lookupObject<compressible::RASModel>("RASProperties");

        return ras.devRhoReff();
    }
    else if (obr_.foundObject<incompressible::RASModel>("RASProperties"))
    {
        const incompressible::RASModel& ras
            = obr_.lookupObject<incompressible::RASModel>("RASProperties");

        return rho()*ras.devReff();
        Info << "XXXXXXXXXXXXX"<< nl;
    }
    else if (obr_.foundObject<compressible::LESModel>("LESProperties"))
    {
        const compressible::LESModel& les =
        obr_.lookupObject<compressible::LESModel>("LESProperties");

        return les.devRhoReff();
    }
    else if (obr_.foundObject<incompressible::LESModel>("LESProperties"))
    {
        const incompressible::LESModel& les
            = obr_.lookupObject<incompressible::LESModel>("LESProperties");

        return rho()*les.devReff();
    }
    else if (obr_.foundObject<fluidThermo>("thermophysicalProperties"))
    {
        const fluidThermo& thermo =
             obr_.lookupObject<fluidThermo>("thermophysicalProperties");

        const volVectorField& U = obr_.lookupObject<volVectorField>(UName_);

        return -thermo.mu()*dev(twoSymm(fvc::grad(U)));
    }
    else if
    (
        obr_.foundObject<transportModel>("transportProperties")
    )
    {
        const transportModel& laminarT =
            obr_.lookupObject<transportModel>("transportProperties");

        const volVectorField& U = obr_.lookupObject<volVectorField>(UName_);

        return -rho()*laminarT.nu()*dev(twoSymm(fvc::grad(U)));
    }
    else if (obr_.foundObject<dictionary>("transportProperties"))
    {
        const dictionary& transportProperties =
             obr_.lookupObject<dictionary>("transportProperties");

        dimensionedScalar nu(transportProperties.lookup("nu"));

        const volVectorField& U = obr_.lookupObject<volVectorField>(UName_);

        return -rho()*nu*dev(twoSymm(fvc::grad(U)));
    }
    else
    {
        FatalErrorIn("power::devRhoReff()")
            << "No valid model for viscous stress calculation"
            << exit(FatalError);

        return volSymmTensorField::null();
    }
}

// Bestimmung der dynamischen Viskositaet
Foam::tmp<Foam::volScalarField> Foam::power::mu() const
{
    if (obr_.foundObject<fluidThermo>("thermophysicalProperties"))
    {
        const fluidThermo& thermo =
             obr_.lookupObject<fluidThermo>("thermophysicalProperties");

        return thermo.mu();
    }
    else if
    (
        obr_.foundObject<singlePhaseTransportModel>("transportProperties")
    )
    {
        const transportModel& laminarT =
            obr_.lookupObject<transportModel>
            ("transportProperties");

        return rho()*laminarT.nu();
    }
    else if (obr_.foundObject<dictionary>("transportProperties"))
    {
        const dictionary& transportProperties =
             obr_.lookupObject<dictionary>("transportProperties");

        dimensionedScalar nu(transportProperties.lookup("nu"));

        return rho()*nu;
    }
    else
    {
        FatalErrorIn("power::mu()")
            << "No valid model for dynamic viscosity calculation"
            << exit(FatalError);

        return volScalarField::null();
    }
}

// Bestimmung der Dichte
Foam::tmp<Foam::volScalarField> Foam::power::rho() const
{
    if (rhoName_ == "rhoInf")
    {
        const fvMesh& mesh = refCast<const fvMesh>(obr_);

        return tmp<volScalarField>
        (
            new volScalarField
            (
                IOobject
                (
                    "rho",
                    mesh.time().timeName(),
                    mesh
                ),
                mesh,
                dimensionedScalar("rho", dimDensity, rhoRef_)
            )
        );
    }
    else
    {
        return(obr_.lookupObject<volScalarField>(rhoName_));
    }
}


Foam::scalar Foam::power::rho(const volScalarField& p) const
{
    if (p.dimensions() == dimPressure)
    {
        return 1.0;
    }
    else
    {
        if (rhoName_ != "rhoInf")
        {
            FatalErrorIn("power::rho(const volScalarField& p)")
                << "Dynamic pressure is expected but kinematic is provided."
                << exit(FatalError);
        }

        return rhoRef_;
    }
}


void Foam::power::applyBins
(
    const vectorField& Power
)
{
        power_[0][0] += sum(Power);
}


void Foam::power::writeBins() const
{
    if (nBin_ == 1)
    {
        return;
    }

}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::power::power
(
    const word& name,
    const objectRegistry& obr,
    const dictionary& dict,
    const bool loadFromFiles
)
:
    functionObjectFile(obr, name, word(dict.lookup("type"))),
    name_(name),
    obr_(obr),
    active_(true),
    log_(false),
    power_(3),
    patchSet_(),
    pName_(word::null),
    UName_(word::null),
    rhoName_(word::null),
    rhoRef_(VGREAT),
    pRef_(0),
    nBin_(1)
 {
    // Check if the available mesh is an fvMesh otherise deactivate
    if (!isA<fvMesh>(obr_))
    {
        active_ = false;
        WarningIn
        (
            "Foam::power::power"
            "("
                "const word&, "
                "const objectRegistry&, "
                "const dictionary&, "
                "const bool"
            ")"
        )   << "No fvMesh available, deactivating."
            << endl;
    }

    read(dict);
}


Foam::power::power
(
    const word& name,
    const objectRegistry& obr,
    const labelHashSet& patchSet,
    const word& pName,
    const word& UName,
    const word& rhoName,
    const scalar rhoInf,
    const scalar pRef
)
:
    functionObjectFile(obr, name, typeName),
    name_(name),
    obr_(obr),
    active_(true),
    log_(false),
    power_(3),
    patchSet_(patchSet),
    pName_(pName),
    UName_(UName),
    rhoName_(rhoName),
    rhoRef_(rhoInf),
    pRef_(pRef),
    nBin_(1){
    forAll(power_, i)
    {
        power_[i].setSize(nBin_);
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::power::~power()
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::power::read(const dictionary& dict)
{
    if (active_)
    {
        log_ = dict.lookupOrDefault<Switch>("log", false);

        const fvMesh& mesh = refCast<const fvMesh>(obr_);
        const polyBoundaryMesh& pbm = mesh.boundaryMesh();

        patchSet_ = pbm.patchSet(wordReList(dict.lookup("patches")));

        {
            // Optional entries U and p
            pName_ = dict.lookupOrDefault<word>("pName", "p");
            UName_ = dict.lookupOrDefault<word>("UName", "U");
            rhoName_ = dict.lookupOrDefault<word>("rhoName", "rho");

            // Check whether UName, pName and rhoName exists,
            // if not deactivate power
            if
            (
                !obr_.foundObject<volVectorField>(UName_)
             || !obr_.foundObject<volScalarField>(pName_)
             || (
                    rhoName_ != "rhoInf"
                 && !obr_.foundObject<volScalarField>(rhoName_)
                )
            )
            {
                active_ = false;

                WarningIn("void power::read(const dictionary&)")
                    << "Could not find " << UName_ << ", " << pName_;

                if (rhoName_ != "rhoInf")
                {
                    Info<< " or " << rhoName_;
                }

                Info<< " in database." << nl
                    << "    De-activating power." << endl;
            }

            // Reference density needed for incompressible calculations
            rhoRef_ = readScalar(dict.lookup("rhoInf"));

            // Reference pressure, 0 by default
            pRef_ = dict.lookupOrDefault<scalar>("pRef", 0.0);
        }

        // allocate storage for power and moments
        power_[0].setSize(1);
        power_[1].setSize(1);
        power_[2].setSize(1);
    }
}


void Foam::power::execute()
{
    // Do nothing - only valid on write
}


void Foam::power::end()
{
    // Do nothing - only valid on write

}

void Foam::power::timeSet()
{
    // Do nothing - only valid on write
}


void Foam::power::write()
{
    if (!active_)
    {
        return;
    }

    calcPower();

    if (Pstream::master())
    {
        functionObjectFile::write();

        //Ausschrieb in das log-file
        if (log_)  
        {
            Info<< type() << " output:" << nl
                << "    power(total, pressure, viscous) = "
                << sum(power_[0]) << nl;
        }

        //Ausschrieb in postProcessing/power...
        file() << obr_.time().value() << tab
            << sum(power_[0]) << endl;

        writeBins();

        if (log_)
        {
            Info<< endl;
        }
    }
}


void Foam::power::calcPower()
{
    power_[0] = vector::zero;
    power_[1] = vector::zero;
    power_[2] = vector::zero;

    {
        const volVectorField& U = obr_.lookupObject<volVectorField>(UName_);
        const volScalarField& p = obr_.lookupObject<volScalarField>(pName_);

        const fvMesh& mesh = U.mesh();
        
        // Bestimmung der Oberflaechenvektoren des patches
        const surfaceVectorField::GeometricBoundaryField& Sfb =
            mesh.Sf().boundaryField();

        // Bestimmung des Extraspannungstensors auf der Oberflaeche des patches
        // devRhoReffb
        tmp<volSymmTensorField> tdevRhoReff = devRhoReff();
        const volSymmTensorField::GeometricBoundaryField& devRhoReffb
            = tdevRhoReff().boundaryField();

        // Scale pRef by density for incompressible simulations
        scalar pRef = pRef_/rho(p);
        
        // Schleife ueber die Oberflaechen eines patches
        forAllConstIter(labelHashSet, patchSet_, iter)
        {
            label patchI = iter.key();

            // Kraftberechnung
            // Normalkraft durch Druck
            vectorField fN
            (
                rho(p)*Sfb[patchI]*(p.boundaryField()[patchI] - pRef)
            );
            // Tangentialkraft durch viskose Effekte
            vectorField fT(Sfb[patchI] & devRhoReffb[patchI]);

            // Leistungsberechnung
            // Gesamtleistung (1. Komponente)
            vector HHH = vector(1,0,0);
            vectorField powerTotal
            (
                - ( (fN+fT) & U.boundaryField()[patchI] ) * HHH
            );
            // Leistung durch Druck (2. Komponente)
            HHH = vector(0,1,0);
            vectorField powerPressure
            (
                - ( fN & U.boundaryField()[patchI] ) * HHH
            );
            // Leistung durch viskose Effekte (3. Komponente)
            HHH = vector(0,0,1);
            vectorField powerViscous
            (
                - ( fT & U.boundaryField()[patchI] ) * HHH
            );
            // Zusammenfassung der Leistungen in einem Vektor (fN)
            vectorField Power = powerTotal + powerPressure + powerViscous ;

            // Weitergabe der Daten 
            applyBins(Power);

//            Info << "Text"<< U.boundaryField()[patchI]  <<nl;
        }
    }

    Pstream::listCombineGather(power_, plusEqOp<vectorField>());
}


Foam::vector Foam::power::powerEff() const
{
    return sum(power_[0]) + sum(power_[1]) + sum(power_[2]);
}

// ************************************************************************* //
