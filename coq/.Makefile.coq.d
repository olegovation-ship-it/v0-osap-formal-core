theories/BasicTypes.vo theories/BasicTypes.glob theories/BasicTypes.v.beautified theories/BasicTypes.required_vo: theories/BasicTypes.v 
theories/BasicTypes.vio: theories/BasicTypes.v 
theories/BasicTypes.vos theories/BasicTypes.vok theories/BasicTypes.required_vos: theories/BasicTypes.v 
theories/Registry.vo theories/Registry.glob theories/Registry.v.beautified theories/Registry.required_vo: theories/Registry.v theories/BasicTypes.vo
theories/Registry.vio: theories/Registry.v theories/BasicTypes.vio
theories/Registry.vos theories/Registry.vok theories/Registry.required_vos: theories/Registry.v theories/BasicTypes.vos
theories/Guards.vo theories/Guards.glob theories/Guards.v.beautified theories/Guards.required_vo: theories/Guards.v theories/BasicTypes.vo theories/Registry.vo
theories/Guards.vio: theories/Guards.v theories/BasicTypes.vio theories/Registry.vio
theories/Guards.vos theories/Guards.vok theories/Guards.required_vos: theories/Guards.v theories/BasicTypes.vos theories/Registry.vos
theories/Prerequisites.vo theories/Prerequisites.glob theories/Prerequisites.v.beautified theories/Prerequisites.required_vo: theories/Prerequisites.v theories/Registry.vo theories/Guards.vo
theories/Prerequisites.vio: theories/Prerequisites.v theories/Registry.vio theories/Guards.vio
theories/Prerequisites.vos theories/Prerequisites.vok theories/Prerequisites.required_vos: theories/Prerequisites.v theories/Registry.vos theories/Guards.vos
theories/DLE.vo theories/DLE.glob theories/DLE.v.beautified theories/DLE.required_vo: theories/DLE.v theories/BasicTypes.vo theories/Registry.vo theories/Guards.vo
theories/DLE.vio: theories/DLE.v theories/BasicTypes.vio theories/Registry.vio theories/Guards.vio
theories/DLE.vos theories/DLE.vok theories/DLE.required_vos: theories/DLE.v theories/BasicTypes.vos theories/Registry.vos theories/Guards.vos
theories/Residuals.vo theories/Residuals.glob theories/Residuals.v.beautified theories/Residuals.required_vo: theories/Residuals.v theories/Registry.vo theories/Guards.vo theories/DLE.vo
theories/Residuals.vio: theories/Residuals.v theories/Registry.vio theories/Guards.vio theories/DLE.vio
theories/Residuals.vos theories/Residuals.vok theories/Residuals.required_vos: theories/Residuals.v theories/Registry.vos theories/Guards.vos theories/DLE.vos
theories/Observer.vo theories/Observer.glob theories/Observer.v.beautified theories/Observer.required_vo: theories/Observer.v 
theories/Observer.vio: theories/Observer.v 
theories/Observer.vos theories/Observer.vok theories/Observer.required_vos: theories/Observer.v 
theories/Branches.vo theories/Branches.glob theories/Branches.v.beautified theories/Branches.required_vo: theories/Branches.v 
theories/Branches.vio: theories/Branches.v 
theories/Branches.vos theories/Branches.vok theories/Branches.required_vos: theories/Branches.v 
theories/Expansion.vo theories/Expansion.glob theories/Expansion.v.beautified theories/Expansion.required_vo: theories/Expansion.v theories/BasicTypes.vo theories/Registry.vo theories/Guards.vo theories/Prerequisites.vo theories/DLE.vo
theories/Expansion.vio: theories/Expansion.v theories/BasicTypes.vio theories/Registry.vio theories/Guards.vio theories/Prerequisites.vio theories/DLE.vio
theories/Expansion.vos theories/Expansion.vok theories/Expansion.required_vos: theories/Expansion.v theories/BasicTypes.vos theories/Registry.vos theories/Guards.vos theories/Prerequisites.vos theories/DLE.vos
theories/Phase3.vo theories/Phase3.glob theories/Phase3.v.beautified theories/Phase3.required_vo: theories/Phase3.v theories/BasicTypes.vo theories/Registry.vo theories/Guards.vo theories/DLE.vo theories/Residuals.vo theories/Observer.vo theories/Branches.vo
theories/Phase3.vio: theories/Phase3.v theories/BasicTypes.vio theories/Registry.vio theories/Guards.vio theories/DLE.vio theories/Residuals.vio theories/Observer.vio theories/Branches.vio
theories/Phase3.vos theories/Phase3.vok theories/Phase3.required_vos: theories/Phase3.v theories/BasicTypes.vos theories/Registry.vos theories/Guards.vos theories/DLE.vos theories/Residuals.vos theories/Observer.vos theories/Branches.vos
theories/Phase4.vo theories/Phase4.glob theories/Phase4.v.beautified theories/Phase4.required_vo: theories/Phase4.v theories/BasicTypes.vo theories/Observer.vo theories/Branches.vo
theories/Phase4.vio: theories/Phase4.v theories/BasicTypes.vio theories/Observer.vio theories/Branches.vio
theories/Phase4.vos theories/Phase4.vok theories/Phase4.required_vos: theories/Phase4.v theories/BasicTypes.vos theories/Observer.vos theories/Branches.vos
theories/Phase5.vo theories/Phase5.glob theories/Phase5.v.beautified theories/Phase5.required_vo: theories/Phase5.v theories/BasicTypes.vo theories/Phase4.vo
theories/Phase5.vio: theories/Phase5.v theories/BasicTypes.vio theories/Phase4.vio
theories/Phase5.vos theories/Phase5.vok theories/Phase5.required_vos: theories/Phase5.v theories/BasicTypes.vos theories/Phase4.vos
theories/Theorems.vo theories/Theorems.glob theories/Theorems.v.beautified theories/Theorems.required_vo: theories/Theorems.v theories/BasicTypes.vo theories/Registry.vo theories/Guards.vo theories/Prerequisites.vo theories/DLE.vo theories/Residuals.vo theories/Observer.vo theories/Branches.vo theories/Expansion.vo theories/Phase3.vo theories/Phase4.vo theories/Phase5.vo theories/Phase6.vo
theories/Theorems.vio: theories/Theorems.v theories/BasicTypes.vio theories/Registry.vio theories/Guards.vio theories/Prerequisites.vio theories/DLE.vio theories/Residuals.vio theories/Observer.vio theories/Branches.vio theories/Expansion.vio theories/Phase3.vio theories/Phase4.vio theories/Phase5.vio theories/Phase6.vio
theories/Theorems.vos theories/Theorems.vok theories/Theorems.required_vos: theories/Theorems.v theories/BasicTypes.vos theories/Registry.vos theories/Guards.vos theories/Prerequisites.vos theories/DLE.vos theories/Residuals.vos theories/Observer.vos theories/Branches.vos theories/Expansion.vos theories/Phase3.vos theories/Phase4.vos theories/Phase5.vos theories/Phase6.vos
theories/Phase6.vo theories/Phase6.glob theories/Phase6.v.beautified theories/Phase6.required_vo: theories/Phase6.v theories/BasicTypes.vo theories/Phase5.vo
theories/Phase6.vio: theories/Phase6.v theories/BasicTypes.vio theories/Phase5.vio
theories/Phase6.vos theories/Phase6.vok theories/Phase6.required_vos: theories/Phase6.v theories/BasicTypes.vos theories/Phase5.vos
