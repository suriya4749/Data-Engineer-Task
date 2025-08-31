from neo4j import GraphDatabase
from datetime import datetime

class Neo4jLoader:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        self.driver.close()

    def load_profile(self, profile):
        """Insert a profile and link phones/specialities with history."""
        with self.driver.session() as session:
            session.write_transaction(self._create_profile_nodes, profile)

    @staticmethod
    def _create_profile_nodes(tx, profile):
        profile_id = profile["profile_id"]
        name = profile.get("name")
        trust_score = profile.get("trust_score", 0)
        source_name = profile.get("source_name")
        created_at = profile.get("created_at")
        updated_at = profile.get("updated_at") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Merge Person node
        tx.run(
            """
            MERGE (p:Person {profile_id: $profile_id})
            SET p.name = $name, p.trust_score = $trust_score, p.source_name = $source_name,
                p.created_at = coalesce(p.created_at, $created_at),
                p.updated_at = $updated_at
            """,
            profile_id=profile_id,
            name=name,
            trust_score=trust_score,
            source_name=source_name,
            created_at=created_at,
            updated_at=updated_at
        )

        # Merge Phone node and relationship
        phone = profile.get("phone")
        if phone:
            tx.run(
                """
                MERGE (ph:Phone {number: $phone})
                MERGE (p:Person {profile_id: $profile_id})
                MERGE (p)-[r:HAS_PHONE]->(ph)
                SET r.created_at = coalesce(r.created_at, $created_at),
                    r.updated_at = $updated_at
                """,
                profile_id=profile_id,
                phone=phone,
                created_at=created_at,
                updated_at=updated_at
            )

        # Merge Specialities nodes and relationships
        for speciality in profile.get("specialities", []):
            tx.run(
                """
                MERGE (s:Speciality {name: $speciality})
                MERGE (p:Person {profile_id: $profile_id})
                MERGE (p)-[r:HAS_SPECIALITY]->(s)
                SET r.created_at = coalesce(r.created_at, $created_at),
                    r.updated_at = $updated_at
                """,
                profile_id=profile_id,
                speciality=speciality,
                created_at=created_at,
                updated_at=updated_at
            )
